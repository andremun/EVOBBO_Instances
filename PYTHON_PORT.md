# Python port

This document records what the Python port (the `evobbo_instances`
package) covers. It records how the port checked its output against
MATLAB. It also records a MATLAB bug that had to be fixed first, before
that check could happen.

## Status

Implemented: `clustergallagher`, `langdonpoli`, `munozsmithmiles`. The
repository is organized by platform. MATLAB code is in `matlab/`. The
Python port is in `python/evobbo_instances/`. Both read the shared
`.mat` data in `data/`. Not ported: `matlab/bbob.v13.09/` (see
[Recommendation](#recommendation)).

| File | Port status | Notes |
|---|---|---|
| `data/*.mat` data files | No conversion needed | `scipy.io.loadmat` reads them directly. |
| `matlab/clustergallagher.m` | Ported, `python/evobbo_instances/clustergallagher.py` | Uses `scipy.spatial.distance.cdist` in place of the embedded `L2_distance` helper. |
| `matlab/langdonpoli.m` | Ported, `python/evobbo_instances/langdonpoli.py` | Direct line-by-line translation of the 19 closed-form functions. |
| `matlab/munozsmithmiles.m` | Ported, `python/evobbo_instances/munozsmithmiles.py` | Needed a small expression parser, see below. |
| `matlab/bbob.v13.09/` | Not ported | Superseded by the official [COCO/BBOB platform](https://github.com/numbbo/coco), which already ships a Python interface. |

## A MATLAB bug had to be fixed first

Porting `matlab/munozsmithmiles.m` meant producing known-correct MATLAB
output first, to check the Python port against. That work found two
bugs in the shipped function. Both bugs made every call fail:

1. The cache check was `if isempty('evalstr')`, testing the 7-character
   string literal `'evalstr'` (never empty) instead of the variable
   `evalstr` (empty on the first call). The cached branch that loads
   `munozsmithmiles.mat` and reads the expression list never ran.
2. Because of bug 1, `evalstr` stayed empty. `Y = feval(evalstr{fid},
   X')` then tried to index an empty value with `{fid}`. MATLAB and
   Octave both reject that.
3. Even with bug 1 fixed, `feval` on the stored value does not work
   either. Each stored individual is a `char` expression string, for
   example `"plus(X(1,:),X(2,:))"`, not a function handle. `feval`
   needs a function name or a handle, not an arbitrary expression. The
   fix is `eval`, not `feval`.
4. Two functions the stored expressions call, `square` and `negexp`,
   are not MATLAB or Octave built-ins. This repository did not include
   them anywhere. They are standard building-block names from the
   genetic programming toolbox (GPTIPS) that generated these
   expressions: `square(x) = x.^2`, `negexp(x) = exp(-x)`. Both are now
   in this repository as `matlab/square.m` and `matlab/negexp.m`.

`matlab/munozsmithmiles.m` in this repository now has all four fixes.
See its version history comment for details. It also has a caching
fix. The original cache never reloaded when `sid` or `d` changed
between calls. This silently reused the wrong expression list. The
cache now uses `(sid, d)` as its key, so this no longer happens.

The `.mat` file stores a small number of individuals (`s2d10` `fid` 2,
41, and 54) as an empty value instead of an expression. Both
`matlab/munozsmithmiles.m` and
`python/evobbo_instances/munozsmithmiles.py` now raise a clear error
for these. Neither silently produces a wrong-shaped or wrong-valued
result.

## The `munozsmithmiles.mat` expression grammar

Every one of the 1520 stored expressions uses only:

- The binary functions `plus`, `minus`, `times`
- The unary functions `exp`, `negexp`, `cos`, `sin`, `square`, `tanh`
- Row indexing, `X(1,:)`, `X(2,:)`, ... up to the instance's dimension
- Numeric literals in brackets, for example `[-10.4887]`

`python/evobbo_instances/_expr.py` parses this grammar with a small
hand-written tokenizer and recursive-descent parser, then evaluates the
parsed tree with `numpy`. It never calls Python's `eval()` on the
stored strings. A parser that only recognizes this fixed grammar cannot
execute anything else. A regex-substitution-plus-`eval()` approach
could not guarantee that as cleanly.

## Validation

This port first produced the fixtures without a MATLAB license, with
GNU Octave 8.4.0. None of the three ported functions uses a toolbox or
a MATLAB-specific language feature, so Octave runs them unmodified.

`tests/generate_fixtures.m` is the checked-in script that produces
`tests/fixtures/*.csv`. It uses `tests/fixtureInputs.m`'s fixed,
deterministic inputs, not random numbers. This means the fixtures do
not depend on the RNG implementation of whichever MATLAB-compatible
environment runs them. Both scripts resolve `matlab/` and `data/`
relative to their own location, so they run from anywhere.

`python/tests/test_*.py` load those fixtures. They check every value
against the Python port's output. They also check the error cases: an
out-of-range `fid`, an invalid `sid`, a mismatched `X` shape, and the 3
empty `munozsmithmiles` individuals. 288 checks pass as of this port.

**Re-validated continuously against real MATLAB.** `matlab/tests/`
holds `matlab.unittest.TestCase` classes. `.github/workflows/matlab-tests.yml`
runs them on every push and pull request. They re-run
`matlab/munozsmithmiles.m`, `matlab/langdonpoli.m`, and
`matlab/clustergallagher.m` on real MATLAB, against the same
`tests/fixtures/*.csv` the Python tests check.

This closes a caveat that was open before: whether Octave and real
MATLAB agree on these three functions. That question is no longer a
"not yet confirmed" note. CI checks it on every commit. If MATLAB CI
and the committed fixtures ever disagree, regenerate the fixtures from
MATLAB, not Octave. Treat any resulting difference as a genuine
Octave/MATLAB behavior gap. Investigate it. Do not dismiss it as noise.

## Dimension guards (2026)

Both languages now validate input shape explicitly, in every function
that previously did not:

- `munozsmithmiles`: `X` must have exactly `d` rows. Before this guard,
  MATLAB silently used only the first `d` rows of a wider `X` (the
  Python port already validated this).
- `langdonpoli`: `X` must have exactly 2 rows (same MATLAB gap, same
  fix).
- `clustergallagher`: `X`'s row count must be a multiple of `dataset`'s
  feature count `p`. The Python port already validated this. MATLAB
  previously only failed by accident, when `reshape` errored on a
  non-integer `k`. `clustergallagher` also now warns, in both
  languages, when `dataset` has more columns than rows, the shape an
  accidental transpose produces.

None of these change behavior for a correct call. Each turns a
previously silent wrong answer, or an unhelpfully generic error, into a
clear error that names the actual problem.

## `clustergallagher`'s `dataset` orientation (2026, breaking change)

`dataset` used to be `(p, n)`. Every caller had to transpose the native
`(n, p)` `data` array from the `.mat`/`.csv` files before calling:
`clustergallagher(X, data')` in MATLAB, `clustergallagher(X, data.T)`
in Python. Both languages now accept `dataset` as `(n, p)` directly.
Each transposes it internally, to reach the same numbers the rest of
the function already worked with.

The internal computation is unchanged, so this is a calling-convention
change, not a numerical one. The existing
`tests/fixtures/clustergallagher.csv` reference values are still
correct after the change. A re-run of `tests/generate_fixtures.m`
confirms this: the output shows no change.

A caller who still transposes under the old convention is not silently
wrong in the typical case. `dataset`'s swapped shape almost never
divides `X`'s row count evenly, so the `kp % p` guard above catches it.

## Data files also mirror to CSV (2026)

Every `.mat` file in `data/` (the 22 numeric datasets and
`munozsmithmiles.mat`) now has a CSV mirror of the same name.
`data/export_to_csv.py` generates these mirrors. They sit alongside the
`.mat` files. They do not replace them.

The numeric datasets round-trip exactly. A check confirmed this,
NaN-aware, against every value. `munozsmithmiles.csv` is a long-format
`(sid, d, fid, expression)` table. It covers all 1520 stored
individuals. A check confirmed this too, row-for-row against the `.mat`
file's six cell arrays.

Neither loader (`munozsmithmiles.m` / `.py`) reads the CSV form yet. It
exists for cross-platform use and for a human to read directly. See the
README's Datasets section.

## Scalability with dimensionality (2026 investigation)

`d` itself is not a free scaling parameter for any of these three
functions. `munozsmithmiles` only has stored expressions for `d` in
`{2, 10}`. `langdonpoli` is defined in 2D only. `clustergallagher`'s
problem dimensionality is `k * p`, with `p` fixed by whichever dataset
is passed in.

The rest of this section reports what does scale. Each claim below
comes from a direct measurement, in Python, in this repository's
sandbox, on 4 cores, not from an assumption.

**`munozsmithmiles`: parsing dominated repeated-call cost.** An
optimizer that calls `munozsmithmiles()` once per iteration, with a
fixed `(sid, d, fid)`, re-parsed the same expression string from
scratch on every call.

Measured cost: 617 us per call, for 2000 repeated single-candidate
calls. In contrast, a single batched call (`X` with `N=2000` columns)
cost only 0.4 us per candidate. At that extreme, parsing cost roughly
1500 times more than evaluation. A direct test isolated the two steps
to confirm this. Parsing that 604-character expression cost 388 us.
Evaluating the same, already-parsed tree cost 83 us.

Fix: `_expr.py` now exposes `parse_expression()` and `evaluate_tree()`
as separate functions. `munozsmithmiles.py` now caches the parsed tree,
keyed on `(data_dir, sid, d, fid)`, alongside the existing
per-`(sid, d)` expression-list cache. This is pure caching. It does not
change any computed value, and all 290 tests still pass.

Measured after the fix: 109 us per call, for the same repeated-call
benchmark. This is a 5.7 times improvement.

`matlab/munozsmithmiles.m` has the same underlying cost: `eval()` also
re-parses the expression on every call. MATLAB has no direct equivalent
to caching a parsed AST. `str2func` on the expression string could
plausibly give a comparable win, by compiling the expression once into
a reusable function handle. This repository does not implement that
yet. It is a follow-up worth prototyping and measuring, not a change to
assume works.

**`clustergallagher`: two vectorization approaches were tested and
rejected. A third is viable, but only as an opt-in choice.** This
repository tested all three against its largest dataset, `skin.mat`
(n=245057, p=3):

- A k-d tree (`scipy.spatial.cKDTree`), built on the k cluster centers
  and queried with all n dataset points, sounds like the right
  structure for a nearest-neighbor problem. It was **6-13x slower**
  than the existing brute-force `cdist`: 52.9 ms/candidate versus
  3.96-6.13 ms/candidate, measured across two runs. The reason: k is
  always small here, a handful of cluster centers. Building and
  querying a tree for that few points gains nothing over `cdist`'s
  single BLAS-backed matrix operation. Rejected.
- Batching several candidates into one manually broadcast distance
  computation trades memory for fewer, larger numpy calls. It was
  **4-60x slower** than the existing per-candidate loop, and it got
  worse as batch size grew: 232.9 ms/candidate at batch size 60, versus
  4.1 ms/candidate for the plain loop. The reason: the naive broadcast
  builds a `(batch, k, n, p)` intermediate array that `cdist`'s own
  implementation avoids. Rejected.

  This result also confirms something empirically.
  `clustergallagher.m`'s own documented choice (v2, 2015) replaced a
  fully vectorized version with this per-candidate loop. That choice
  was not merely a memory compromise. It is close to the actual
  performance optimum for this problem shape.
- Thread-based parallelism across the `N`-candidate loop is possible
  because `cdist` releases the GIL during its BLAS call. On the large
  dataset, with 4 worker threads, it gave a real **2.9x speedup**: 3.6
  ms/candidate down to 1.26 ms/candidate. With 8 threads on 4 physical
  cores, it regressed slightly, as expected from oversubscription. On
  the small `iris.mat` case (n=150), it was **12x slower**: thread-pool
  overhead dominates when per-candidate work is already sub-millisecond.

  This approach helps, but only under the right conditions. It is a
  candidate for an opt-in parameter, for example `max_workers=None`
  meaning today's serial behavior, not a new default. This repository
  does not implement it yet. It would change `clustergallagher`'s
  signature again, so soon after the orientation change above. That
  decision needs agreement first.

**`langdonpoli`: no scaling concern found.** It is already fully
vectorized across `N`, with no per-candidate loop. Measured cost stayed
sub-microsecond per candidate, from `N=100` to `N=1,000,000`.

## Recommendation

Do not port `matlab/bbob.v13.09/`. Point users to the official COCO/BBOB
Python package instead, as the main README already does.
