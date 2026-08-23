"""Python port of munozsmithmiles.m.

Functions generated for the paper "Generating New Space-Filling Test
Instances for Continuous Black-Box Optimization", Evol. Comput., 2019.

munozsmithmiles.mat stores each instance as a MATLAB expression string.
This module parses that grammar directly (see _expr.py). It does not
call MATLAB's eval/feval, which the original .m file used. That
original approach needed two bug fixes (see munozsmithmiles.m's version
history) and two extra helper functions, square.m and negexp.m, before
it would run at all.

tests/test_munozsmithmiles.py validates this module against MATLAB
reference output.
"""

import numpy as np
from scipy.io import loadmat

from ._expr import ExpressionError, evaluate_tree, parse_expression
from ._paths import resolve_data_dir

_VALID_SID = (1, 2, 3)
_VALID_D = (2, 10)

# Cache of loaded expression lists, keyed by (data_dir, sid, d). This
# means repeated calls do not re-read the .mat file. The MATLAB
# source's cache is different (see the fix in this port's companion .m
# file). This cache keys on every input that changes which expressions
# load, so it stays correct when a caller switches sid, d, or data_dir
# between calls.
_CACHE = {}

# Cache of parsed expression trees, keyed by (data_dir, sid, d, fid).
# Parsing an expression string costs roughly 5-10x more than evaluating
# an already-parsed tree. This was measured directly. Longer
# expressions cost proportionally more to parse. An optimizer that
# calls munozsmithmiles() once per iteration, with a fixed
# (sid, d, fid), would otherwise re-parse the same string on every
# call. This cache makes every call after the first skip straight to
# evaluation.
_TREE_CACHE = {}


def _load_expressions(sid, d, data_dir):
    key = (str(data_dir), sid, d)
    if key not in _CACHE:
        if sid not in _VALID_SID or d not in _VALID_D:
            raise ValueError(
                "Either the strategy number or the dimension is incorrect. "
                "Choose a strategy number between 1 and 3 and a dimension "
                "equal to 2 or 10."
            )
        var_name = f"s{sid}d{d}"
        mat_path = data_dir / "munozsmithmiles.mat"
        if not mat_path.is_file():
            raise FileNotFoundError(
                f"munozsmithmiles.mat not found in {data_dir}. If this "
                "package is not running from a source checkout of the "
                "EVOBBO_Instances repository, pass data_dir explicitly."
            )
        mat = loadmat(mat_path, variable_names=[var_name], squeeze_me=True)
        raw = mat[var_name]
        exprs = [e.decode() if isinstance(e, bytes) else str(e) for e in np.atleast_1d(raw)]
        _CACHE[key] = exprs
    return _CACHE[key]


def munozsmithmiles(X, sid, d, fid, data_dir=None):
    """Evaluate one generated instance from Munoz & Smith-Miles (2019).

    Args:
        X: array_like of shape (d, N), candidate solutions.
        sid: strategy id, an integer from 1 to 3.
        d: function dimension, 2 or 10.
        fid: function id. The valid range depends on (sid, d):
            s1d2 <= 600, s1d10 <= 120, s2d2 <= 100, s2d10 <= 500,
            s3d2 <= 100, s3d10 <= 100.
        data_dir: directory that holds munozsmithmiles.mat. Defaults to
            the repository's data/ directory.

    Returns:
        A numpy array of shape (N,) with one fitness value per column
        of X.

    Raises:
        FileNotFoundError: if data_dir (or its default, the repository's
            data/ directory) does not exist or does not contain
            munozsmithmiles.mat. The default only resolves correctly
            when this package runs from a source checkout of the
            repository. Otherwise, pass data_dir explicitly.
        ValueError: if sid, d, or fid is out of range.
        ExpressionError: if the requested individual has no expression
            (a small number of individuals, all in s2d10, are empty).
    """
    data_dir = resolve_data_dir(data_dir)
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] != d:
        raise ValueError(f"X must have shape ({d}, N) to match d={d}, got {X.shape}")

    exprs = _load_expressions(sid, d, data_dir)
    nfunc = len(exprs)
    if not (1 <= fid <= nfunc):
        raise ValueError(
            f"Function index {fid} is invalid. "
            f"Only {nfunc} functions exist in experiment s{sid}d{d}."
        )

    tree_key = (str(data_dir), sid, d, fid)
    try:
        tree = _TREE_CACHE[tree_key]
    except KeyError:
        try:
            tree = parse_expression(exprs[fid - 1])
        except ExpressionError as exc:
            raise ExpressionError(
                f"Function {fid} in experiment s{sid}d{d} has no expression "
                f"(empty individual): {exc}"
            ) from exc
        _TREE_CACHE[tree_key] = tree

    return evaluate_tree(tree, X)
