# Python port: feasibility assessment

This document scopes a Python port of this repository. It records what a
port needs, per file, and an effort estimate. No Python code exists yet in
this repository. This is a planning document, not an implementation.

## Summary

A Python port of the three instance-generating functions is low effort,
roughly 2-3 days for one developer, including tests. The data files need
no conversion. The `bbob.v13.09/` folder should not be ported. See
[Recommendation](#recommendation).

| File | Port effort | Why |
|---|---|---|
| `*.mat` data files | None | `scipy.io.loadmat` reads them directly. |
| `clustergallagher.m` | Low (a few hours) | Standard vectorized distance computation, direct `numpy`/`scipy.spatial` equivalent. |
| `langdonpoli.m` | Low (a few hours) | A fixed list of 19 closed-form polynomial and trigonometric functions. Direct line-by-line translation. |
| `munozsmithmiles.m` | Medium (1-2 days) | Needs a small expression transpiler (see below). The hard part of this port. |
| `bbob.v13.09/` | Not recommended | Superseded by the official [COCO/BBOB platform](https://github.com/numbbo/coco), which already ships a Python interface. |

## Per-file detail

### `clustergallagher.m`

Reshapes `X` into `k` candidate cluster centers of dimensionality `p`,
computes the pairwise Euclidean distance between each dataset point and
each candidate center, and sums the squared distance to the nearest
center. This maps directly onto `scipy.spatial.distance.cdist` inside a
loop over the `N` candidate solutions, or a vectorized `numpy` broadcast.
The embedded `L2_distance` helper (credited to Roland Bunschoten and
Laurens van der Maaten, for non-commercial use, see the file header) is
replaced outright by `scipy.spatial.distance.cdist`, which computes the
same quantity. No behavior needs to be reproduced by hand.

### `langdonpoli.m`

A literal MATLAB cell array of 19 anonymous functions, each a short
polynomial or trigonometric expression in two variables. Each one
translates to a Python `lambda` or a plain function using `numpy`
elementwise operations. The bound check (`Y = 0` where `|X| > 10`) also
translates directly with `numpy.where`.

### `munozsmithmiles.m`

`munozsmithmiles.mat` stores 1520 instance definitions as MATLAB
expression strings, evaluated at run time through MATLAB's `eval`. For
example:

```
plus(plus(minus(...),X(1,:)),plus(tanh(...),...))
```

Every expression in the file uses only the following building blocks:

- Arithmetic: `plus`, `minus`, `times`
- Elementwise functions: `exp`, `negexp`, `cos`, `sin`, `square`, `tanh`
- Indexing: `X(1,:)`, `X(2,:)`
- Numeric literals in brackets: `[-10.4887]`
- The empty expression `[]` (a small number of instances are empty and
  should evaluate to a constant or be filtered out)

A Python port needs a small parser or transpiler for this grammar, not a
full MATLAB interpreter. Two viable approaches:

1. **Recursive-descent parser.** Parse the string into an expression
   tree, then evaluate it with `numpy` functions
   (`numpy.exp`, `numpy.cos`, `numpy.sin`, `numpy.tanh`, `X[0, :]`,
   `X[1, :]`, and `numpy.square` for `square`, plus `negexp(x) =
   numpy.exp(-x)`). This is the recommended approach: it never calls
   `eval` on the stored strings.
2. **Regex substitution into a Python expression, then `eval`.** Faster
   to write, but calls `eval` on parsed file content. Because the
   `.mat` file ships in this repository and is not user input, the risk
   is low, but a parser (option 1) removes the risk entirely and should
   be preferred for a public package.

`scipy.io.loadmat(..., squeeze_me=True)` reads the string array
(`s1d2`, `s1d10`, `s2d2`, `s2d10`, `s3d2`, `s3d10`) directly, with no
extra conversion of the `.mat` file needed.

### `bbob.v13.09/`

This is a vendored copy of the COCO/BBOB v13.09 MATLAB platform from
2011, kept only as a historical reference (the file `benchmarks.m`
implements the original 24 noiseless BBOB functions). The current
[COCO/BBOB platform](https://github.com/numbbo/coco) already ships an
official, maintained Python interface (the `cocoex` package). Porting
this folder would duplicate that maintained implementation. See
[Recommendation](#recommendation).

## Recommendation

Port `clustergallagher.m`, `langdonpoli.m`, and `munozsmithmiles.m` into a
small `evobbo_instances` Python package:

```
evobbo_instances/
├── __init__.py
├── clustergallagher.py
├── langdonpoli.py
├── munozsmithmiles.py       # expression parser and evaluator
├── data/                     # the existing .mat files, unchanged
tests/
├── test_clustergallagher.py  # compare against MATLAB reference output
├── test_langdonpoli.py
└── test_munozsmithmiles.py
requirements.txt              # numpy, scipy
```

Do not port `bbob.v13.09/`. Point users to the official COCO/BBOB Python
package instead, as the main README already does.

For every ported function, validate the Python output against fixed
MATLAB reference output (a small CSV per function, generated once from
MATLAB and checked into `tests/`), following the cross-language
validation pattern used elsewhere in this research program: record which
commit of the MATLAB code generated each fixture, so a future MATLAB
change does not silently invalidate the fixture.
