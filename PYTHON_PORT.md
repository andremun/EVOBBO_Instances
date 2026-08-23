# Python port

This document records what the Python port (the `evobbo_instances`
package) covers, how its output was checked against MATLAB, and what a
MATLAB bug fix had to happen first to make that check possible.

## Status

Implemented: `clustergallagher`, `langdonpoli`, `munozsmithmiles`. The
repository is organized by platform: MATLAB code is in `matlab/`, the
Python port is in `python/evobbo_instances/`, and the shared `.mat` data
both read is in `data/`. Not ported: `matlab/bbob.v13.09/` (see
[Recommendation](#recommendation)).

| File | Port status | Notes |
|---|---|---|
| `data/*.mat` data files | No conversion needed | `scipy.io.loadmat` reads them directly. |
| `matlab/clustergallagher.m` | Ported, `python/evobbo_instances/clustergallagher.py` | Uses `scipy.spatial.distance.cdist` in place of the embedded `L2_distance` helper. |
| `matlab/langdonpoli.m` | Ported, `python/evobbo_instances/langdonpoli.py` | Direct line-by-line translation of the 19 closed-form functions. |
| `matlab/munozsmithmiles.m` | Ported, `python/evobbo_instances/munozsmithmiles.py` | Needed a small expression parser, see below. |
| `matlab/bbob.v13.09/` | Not ported | Superseded by the official [COCO/BBOB platform](https://github.com/numbbo/coco), which already ships a Python interface. |

## A MATLAB bug had to be fixed first

Porting `matlab/munozsmithmiles.m` meant generating known-correct MATLAB output
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
   in this repository as `matlab/square.m` and `matlab/negexp.m`.

`matlab/munozsmithmiles.m` in this repository now has all four fixes
(see its version history comment), plus a caching fix: the original
cache also never reloaded when `sid` or `d` changed between calls,
silently reusing the wrong expression list. This is fixed by keying the
cache on `(sid, d)`. `matlab/square.m` and `matlab/negexp.m` were added
alongside it. A small number of individuals (`s2d10` `fid` 2, 41, and
54) are stored as an empty value rather than an expression; both
`matlab/munozsmithmiles.m` and `python/evobbo_instances/munozsmithmiles.py`
now raise a clear error for these instead of silently producing a
wrong-shaped or wrong-valued result.

## The `munozsmithmiles.mat` expression grammar

Every one of the 1520 stored expressions uses only:

- The binary functions `plus`, `minus`, `times`
- The unary functions `exp`, `negexp`, `cos`, `sin`, `square`, `tanh`
- Row indexing, `X(1,:)`, `X(2,:)`, ... up to the instance's dimension
- Numeric literals in brackets, for example `[-10.4887]`

`python/evobbo_instances/_expr.py` parses this grammar with a small
hand-written tokenizer and recursive-descent parser, then evaluates the
parsed tree with `numpy`. It never calls Python's `eval()` on the
stored strings: a parser that only recognizes this fixed grammar cannot
execute anything else, which a regex-substitution-plus-`eval()`
approach could not guarantee as cleanly.

## Validation

The fixtures were first produced without a MATLAB license, using GNU
Octave 8.4.0 (none of the three ported functions uses a toolbox or a
MATLAB-specific language feature, so Octave runs them unmodified).
`tests/generate_fixtures.m` is the checked-in script that produces
`tests/fixtures/*.csv` from `tests/fixtureInputs.m`'s fixed,
deterministic inputs (not random numbers, so the fixtures do not depend
on the RNG implementation of whichever MATLAB-compatible environment
runs them); both scripts resolve `matlab/` and `data/` relative to their
own location, so they run from anywhere. `python/tests/test_*.py` load
those fixtures and check every value against the Python port's output,
plus the error cases (out-of-range `fid`, invalid `sid`, mismatched `X`
shape, the 3 empty `munozsmithmiles` individuals). 288 checks pass as of
this port.

**Re-validated continuously against real MATLAB.** `matlab/tests/`
(`matlab.unittest.TestCase` classes, run by
`.github/workflows/matlab-tests.yml` on every push and pull request)
re-runs `matlab/munozsmithmiles.m`, `matlab/langdonpoli.m`, and
`matlab/clustergallagher.m` on real MATLAB against the same
`tests/fixtures/*.csv` the Python tests check. This closes what was
previously an open caveat here: whether Octave and real MATLAB agree on
these three functions is no longer a "not yet confirmed" note, it is
checked on every commit. If MATLAB CI and the committed fixtures ever
disagree, regenerate the fixtures from MATLAB (not Octave) and treat any
resulting diff as a genuine Octave/MATLAB behavior gap to investigate,
not as noise to paper over.

## Dimension guards (2026)

Both languages now validate input shape explicitly, in every function
that previously did not:

- `munozsmithmiles`: `X` must have exactly `d` rows. Before this guard,
  MATLAB silently used only the first `d` rows of a wider `X` (the
  Python port already validated this).
- `langdonpoli`: `X` must have exactly 2 rows (same MATLAB gap, same
  fix).
- `clustergallagher`: `X`'s row count must be a multiple of `dataset`'s
  feature count `p` (the Python port already validated this; MATLAB
  previously only failed incidentally, through `reshape` erroring on a
  non-integer `k`). `clustergallagher` also now warns, in both
  languages, when `dataset` has more columns than rows: unusual for
  these benchmark datasets, and exactly what an accidental transpose
  looks like.

None of these change behavior for a correct call. Each turns a
previously silent wrong answer, or an unhelpfully generic error, into a
clear one naming the actual problem.

## `clustergallagher`'s `dataset` orientation (2026, breaking change)

`dataset` used to be `(p, n)`, requiring every caller to transpose the
native `(n, p)` `data` array from the `.mat`/`.csv` files before calling
(`clustergallagher(X, data')` in MATLAB, `clustergallagher(X, data.T)`
in Python). Both languages now accept `dataset` as `(n, p)` directly,
transposing it internally to reach the same numbers the rest of the
function already worked with. Because the internal computation is
unchanged, this is a calling-convention change, not a numerical one:
the existing `tests/fixtures/clustergallagher.csv` reference values are
still correct after the change, confirmed by re-running
`tests/generate_fixtures.m` and diffing (no change).

A caller still transposing under the old convention is not silently
wrong in the typical case: `dataset`'s swapped shape almost never
divides `X`'s row count evenly, so the `kp % p` guard above catches it.

## Data files also mirror to CSV (2026)

Every `.mat` file in `data/` (the 22 numeric datasets and
`munozsmithmiles.mat`) now has a CSV mirror of the same name, generated
by `data/export_to_csv.py` and committed alongside the `.mat` files, not
replacing them. The numeric datasets round-trip exactly (verified
NaN-aware against every value); `munozsmithmiles.csv` is a long-format
`(sid, d, fid, expression)` table covering all 1520 stored individuals,
verified row-for-row against the `.mat` file's six cell arrays. Neither
loader (`munozsmithmiles.m` / `.py`) reads the CSV form yet; it exists
for cross-platform and human readability, see the README's Datasets
section.

## Scalability with dimensionality (2026 investigation)

`d` itself is not a free scaling parameter for any of these three
functions: `munozsmithmiles` only has stored expressions for `d` in
`{2, 10}`, `langdonpoli` is defined in 2D only, and `clustergallagher`'s
problem dimensionality is `k * p`, with `p` fixed by whichever dataset
is passed in. What *does* scale, and was profiled directly (Python,
this repository's sandbox, 4 cores) rather than assumed:

**`munozsmithmiles`: parsing dominated repeated-call cost.** An
optimizer calling `munozsmithmiles()` once per iteration with a fixed
`(sid, d, fid)` re-parsed the same expression string from scratch every
call. Measured: 617 us/call for 2000 repeated single-candidate calls,
versus 0.4 us/candidate batched (`X` with `N=2000` columns in one
call) -- parsing was roughly 1500x the cost of evaluation at that
extreme, and isolating the two confirmed it directly (388 us to parse a
604-character expression, versus 83 us to evaluate the same
already-parsed tree). Fixed: `_expr.py` now exposes `parse_expression()`
and `evaluate_tree()` separately, and `munozsmithmiles.py` caches the
parsed tree per `(data_dir, sid, d, fid)`, alongside the existing
per-`(sid, d)` expression-list cache. Measured after the fix: 109
us/call for the same repeated-call benchmark, a 5.7x improvement, pure
caching with no change to any computed value (all 290 tests still
pass). `matlab/munozsmithmiles.m` has the same underlying cost
(`eval()` re-parses every call too); MATLAB has no direct equivalent to
caching a parsed AST, though `str2func` on the expression string could
plausibly give a comparable win by compiling once into a reusable
function handle -- not implemented here, flagged as a follow-up worth
prototyping and measuring, not assumed to work.

**`clustergallagher`: two plausible vectorization approaches, both
measured and rejected; one viable but explicitly opt-in.** All three
tested against the largest dataset in this repository (`skin.mat`,
n=245057, p=3):

- A k-d tree (`scipy.spatial.cKDTree`) built on the k cluster centers,
  queried with all n dataset points, sounds like the right structure
  for a nearest-neighbor problem, but was **6-13x slower** than the
  existing brute-force `cdist` (52.9 ms/candidate vs 3.96-6.13 ms/candidate
  measured across two runs): k is always small here (a handful of
  cluster centers), and building/querying a tree for that few points
  does not amortize against `cdist`'s single BLAS-backed matrix
  operation. Rejected.
- Batching several candidates into one manually-broadcast distance
  computation (trading memory for fewer, larger numpy calls) was
  **4-60x slower** than the existing per-candidate loop, worse as batch
  size grew (232.9 ms/candidate at batch size 60 vs 4.1 ms/candidate for
  the plain loop): the naive broadcast materializes a `(batch, k, n, p)`
  intermediate array that `cdist`'s internal implementation avoids.
  Rejected. This also confirms, empirically, that
  `clustergallagher.m`'s own documented choice (v2, 2015: replace a
  fully vectorized version with this per-candidate loop) was not merely
  a memory compromise; it is close to the actual performance optimum
  for this problem shape.
- Thread-based parallelism across the `N`-candidate loop (`cdist`
  releases the GIL during its BLAS call) gave a real **2.9x speedup**
  with 4 worker threads on the large dataset (3.6 ms/candidate down to
  1.26 ms/candidate; 8 threads on 4 physical cores regressed slightly,
  as expected from oversubscription) -- but was **12x slower** on the
  small `iris.mat` case (n=150): thread-pool overhead dominates when
  per-candidate work is already sub-millisecond. This is genuinely
  useful, but only conditionally, so it is a candidate for an opt-in
  parameter (for example `max_workers=None` meaning today's serial
  behavior), not a default. Not yet implemented; proposed here for a
  decision before adding it, since it changes `clustergallagher`'s
  signature again so soon after the orientation change above.

**`langdonpoli`: no scaling concern found.** Already fully vectorized
across `N` with no per-candidate loop; measured sub-microsecond per
candidate from `N=100` to `N=1,000,000`.

## Recommendation

Do not port `matlab/bbob.v13.09/`. Point users to the official COCO/BBOB
Python package instead, as the main README already does.
