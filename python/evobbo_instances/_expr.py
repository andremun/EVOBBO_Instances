"""Parser and evaluator for the expression grammar in munozsmithmiles.mat.

Each instance in munozsmithmiles.mat is a MATLAB expression string, for
example:

    plus(plus(minus(plus(...),X(1,:)),...),tanh(...))

This module parses that grammar directly and evaluates it with numpy,
rather than calling Python's eval() on untrusted-looking text. The
grammar uses only:

- The binary functions plus, minus, times
- The unary functions exp, negexp, cos, sin, square, tanh
- Indexing into a row of X: X(1,:), X(2,:), and so on
- Numeric literals in brackets, for example [-10.4887]
"""

import re

import numpy as np

_TOKEN_RE = re.compile(
    r"""
    (?P<NUMBER>-?\d+\.?\d*(?:[eE][+-]?\d+)?)
    | (?P<NAME>[A-Za-z_][A-Za-z0-9_]*)
    | (?P<LPAREN>\()
    | (?P<RPAREN>\))
    | (?P<LBRACKET>\[)
    | (?P<RBRACKET>\])
    | (?P<COMMA>,)
    | (?P<COLON>:)
    | (?P<SPACE>\s+)
    """,
    re.VERBOSE,
)

_UNARY_FUNCS = {
    "exp": np.exp,
    "negexp": lambda x: np.exp(-x),
    "cos": np.cos,
    "sin": np.sin,
    "square": np.square,
    "tanh": np.tanh,
}

_BINARY_FUNCS = {
    "plus": np.add,
    "minus": np.subtract,
    "times": np.multiply,
}


class ExpressionError(ValueError):
    """This error means the expression string is malformed or unsupported."""


def _tokenize(expr):
    tokens = []
    pos = 0
    while pos < len(expr):
        m = _TOKEN_RE.match(expr, pos)
        if not m:
            raise ExpressionError(f"Cannot tokenize {expr!r} at position {pos}")
        pos = m.end()
        kind = m.lastgroup
        if kind == "SPACE":
            continue
        tokens.append((kind, m.group(kind)))
    return tokens


class _Parser:
    def __init__(self, tokens, expr):
        self._tokens = tokens
        self._pos = 0
        self._expr = expr

    def _peek(self):
        return self._tokens[self._pos] if self._pos < len(self._tokens) else (None, None)

    def _advance(self):
        tok = self._peek()
        self._pos += 1
        return tok

    def _expect(self, kind):
        tok_kind, tok_val = self._advance()
        if tok_kind != kind:
            raise ExpressionError(
                f"Expected {kind}, got {tok_kind} ({tok_val!r}) in {self._expr!r}"
            )
        return tok_val

    def parse(self):
        node = self._parse_expr()
        if self._pos != len(self._tokens):
            raise ExpressionError(f"Unexpected trailing tokens in {self._expr!r}")
        return node

    def _parse_expr(self):
        kind, val = self._peek()
        if kind == "LBRACKET":
            return self._parse_bracket()
        if kind == "NAME" and val == "X":
            return self._parse_index()
        if kind == "NAME":
            return self._parse_call()
        raise ExpressionError(f"Unexpected token {kind} ({val!r}) in {self._expr!r}")

    def _parse_bracket(self):
        self._expect("LBRACKET")
        kind, _ = self._peek()
        if kind == "RBRACKET":
            raise ExpressionError(
                f"Empty literal [] is not a valid instance expression: {self._expr!r}"
            )
        num = self._expect("NUMBER")
        self._expect("RBRACKET")
        return ("literal", float(num))

    def _parse_index(self):
        self._expect("NAME")  # 'X'
        self._expect("LPAREN")
        row = self._expect("NUMBER")
        self._expect("COMMA")
        self._expect("COLON")
        self._expect("RPAREN")
        return ("index", int(row) - 1)  # MATLAB is 1-based, numpy is 0-based

    def _parse_call(self):
        name = self._expect("NAME")
        self._expect("LPAREN")
        args = [self._parse_expr()]
        while self._peek()[0] == "COMMA":
            self._advance()
            args.append(self._parse_expr())
        self._expect("RPAREN")
        return ("call", name, args)


def _evaluate(node, X):
    kind = node[0]
    if kind == "literal":
        return node[1]
    if kind == "index":
        row = node[1]
        if not (0 <= row < X.shape[0]):
            raise ExpressionError(f"X row index {row + 1} out of range for X with {X.shape[0]} rows")
        return X[row, :]
    if kind == "call":
        _, name, args = node
        values = [_evaluate(a, X) for a in args]
        if name in _UNARY_FUNCS:
            if len(values) != 1:
                raise ExpressionError(f"{name}() expects 1 argument, got {len(values)}")
            return _UNARY_FUNCS[name](values[0])
        if name in _BINARY_FUNCS:
            if len(values) != 2:
                raise ExpressionError(f"{name}() expects 2 arguments, got {len(values)}")
            return _BINARY_FUNCS[name](values[0], values[1])
        raise ExpressionError(f"Unknown function {name!r}")
    raise ExpressionError(f"Unknown node kind {kind!r}")


def parse_expression(expr):
    """Parse one instance expression string into a reusable tree.

    Parsing is the expensive part of evaluating an expression, roughly
    5-10x the cost of evaluating an already-parsed tree, and longer for
    longer expressions. Callers that evaluate the same expression
    repeatedly should parse it once with this function, then reuse the
    tree with evaluate_tree(). One example: munozsmithmiles(), called
    once per optimizer iteration with a fixed (sid, d, fid). Calling
    evaluate_expression() in a loop instead parses the expression every
    time.

    Args:
        expr: the MATLAB expression string, e.g. "plus(X(1,:),X(2,:))".

    Returns:
        An opaque tree object for evaluate_tree().
    """
    expr = expr.strip()
    if not expr or expr == "[]":
        raise ExpressionError("Empty expression (no instance defined)")
    return _Parser(_tokenize(expr), expr).parse()


def evaluate_tree(tree, X):
    """Evaluate a tree from parse_expression() over candidate solutions X.

    Args:
        tree: the return value of parse_expression().
        X: numpy array of shape (d, N).

    Returns:
        A numpy array of shape (N,).
    """
    result = _evaluate(tree, X)
    return np.broadcast_to(np.asarray(result, dtype=float), (X.shape[1],)).copy()


def evaluate_expression(expr, X):
    """Parse and evaluate one instance expression string in one call.

    Convenience wrapper for a single evaluation. Prefer parse_expression()
    plus evaluate_tree() when evaluating the same expr repeatedly: see
    parse_expression()'s docstring.

    Args:
        expr: the MATLAB expression string, e.g. "plus(X(1,:),X(2,:))".
        X: numpy array of shape (d, N).

    Returns:
        A numpy array of shape (N,).
    """
    return evaluate_tree(parse_expression(expr), X)
