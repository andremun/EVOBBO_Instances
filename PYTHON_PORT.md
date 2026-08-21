# Python port

This document records what the Python port (the `evobbo_instances`
package) covers, how its output was checked against MATLAB, and what a
MATLAB bug fix had to happen first to make that check possible.

## Status

Implemented: `clustergallagher`, `langdonpoli`, `munozsmithmiles`.
Not ported: `bbob.v13.09/` (see [Recommendation](#recommendation)).

| File | Port status | Notes |
|---|---|---|
| `*.mat` data files | No conversion needed | `scipy.io.loadmat` reads them directly. |
| `clustergallagher.m` | Ported, `evobbo_instances/clustergallagher.py` | Uses `scipy.spatial.distance.cdist` in place of the embedded `L2_distance` helper. |
| `langdonpoli.m` | Ported, `evobbo_instances/langdonpoli.py` | Direct line-by-line translation of the 19 closed-form functions. |
| `munozsmithmiles.m` | Ported, `evobbo_instances/munozsmithmiles.py` | Needed a small expression parser, see below. |
| `bbob.v13.09/` | Not ported | Superseded by the official [COCO/BBOB platform](https://github.com/numbbo/coco), which already ships a Python interface. |

## A MATLAB bug had to be fixed first

Porting `munozsmithmiles.m` meant generating known-correct MATLAB output
to check the Python port against. Doing that surfaced two bugs in the
shipped function that made every call fail:

1. The cache check was `if isempty('evalstr')`, testing the 7-character
   string literal `'evalstr'` (never empty) instead of the variable
   `evalstr` (empty on the first call). The cached branch that loads
   `munozsmithmiles.mat` and reads the expression list never ran.
2. Because of bug 1, `evalstr` stayed empty, and
   `Y = feval(evalstr{fid}, X')` tried to index an empty value with
   `{fid}`, which MATLAB and Octave both reject.
3. Even with bug 1 fixed, `feval` on the stored value does not work
   either: each stored individual is a `char` expression string (for
   example `"plus(X(1,:),X(2,:))"`), not a function handle, and `feval`
   needs a function name or handle, not an arbitrary expression. The
   fix is `eval`, not `feval`.
4. Two functions the stored expressions call, `square` and `negexp`,
   are not MATLAB or Octave built-ins and were not included anywhere in
   this repository. They are standard building-block names from the
   genetic programming toolbox (GPTIPS) that generated these
   expressions: `square(x) = x.^2`, `negexp(x) = exp(-x)`. Both are now
   in this repository as `square.m` and `negexp.m`.

`munozsmithmiles.m` in this repository now has all four fixes (see its
version history comment), plus a caching fix: the original cache also
never reloaded when `sid` or `d` changed between calls, silently
reusing the wrong expression list. This is fixed by keying the cache on
`(sid, d)`. `square.m` and `negexp.m` were added alongside it. A small
number of individuals (`s2d10` `fid` 2, 41, and 54) are stored as an
empty value rather than an expression; both `munozsmithmiles.m` and
`munozsmithmiles.py` now raise a clear error for these instead of
silently producing a wrong-shaped or wrong-valued result.

## The `munozsmithmiles.mat` expression grammar

Every one of the 1520 stored expressions uses only:

- The binary functions `plus`, `minus`, `times`
- The unary functions `exp`, `negexp`, `cos`, `sin`, `square`, `tanh`
- Row indexing, `X(1,:)`, `X(2,:)`, ... up to the instance's dimension
- Numeric literals in brackets, for example `[-10.4887]`

`evobbo_instances/_expr.py` parses this grammar with a small
hand-written tokenizer and recursive-descent parser, then evaluates the
parsed tree with `numpy`. It never calls Python's `eval()` on the
stored strings: a parser that only recognizes this fixed grammar cannot
execute anything else, which a regex-substitution-plus-`eval()`
approach could not guarantee as cleanly.

## Validation

No MATLAB license was available in the environment this port was built
in. Reference output instead came from GNU Octave 8.4.0, which runs all
three functions unmodified (none uses a toolbox or a MATLAB-specific
language feature). `tests/generate_fixtures.m` is the checked-in script
that produces `tests/fixtures/*.csv` from fixed, deterministic inputs
(not random numbers, so the fixtures do not depend on the RNG
implementation of whichever MATLAB-compatible environment runs them).
`tests/test_*.py` load those fixtures and check every value against the
Python port's output, plus the error cases (out-of-range `fid`, invalid
`sid`, mismatched `X` shape, the 3 empty `munozsmithmiles` individuals).
All 287 checks pass as of this port.

**Re-validate with real MATLAB when available**: re-run
`tests/generate_fixtures.m` in MATLAB and re-run `pytest tests/`. A
difference would point to a real Octave/MATLAB behavior gap in one of
these three functions; none is expected, since they use only core
array arithmetic, but this has not been directly confirmed against
MathWorks MATLAB.

## Recommendation

Do not port `bbob.v13.09/`. Point users to the official COCO/BBOB Python
package instead, as the main README already does.
