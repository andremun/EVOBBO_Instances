# Evolved BBO Instances

[![DOI](https://zenodo.org/badge/198110974.svg)](https://zenodo.org/badge/latestdoi/198110974)
[![MATLAB tests](https://github.com/andremun/EVOBBO_Instances/actions/workflows/matlab-tests.yml/badge.svg)](https://github.com/andremun/EVOBBO_Instances/actions/workflows/matlab-tests.yml)

This repository holds test instances and datasets for continuous
black-box optimization (BBO) research. It supports the paper M.A. Muñoz
and K. Smith-Miles, ["Generating New Space-Filling Test Instances for
Continuous Black-Box Optimization"](https://doi.org/10.1162/evco_a_00262),
Evol. Comput., 2019.

The repository provides instances from four sources:

1. **Generated instances** from the methodology in the paper above, through
   the function `matlab/munozsmithmiles.m` (needs `matlab/square.m` and
   `matlab/negexp.m`; see that function's version history for two bugs
   fixed in 2026 that made every call fail before the fix).
2. **Reference BBOB instances** from the "Comparing Continuous Optimization"
   benchmarking platform v13.09 (2011), in `matlab/bbob.v13.09/`. Use the
   [current COCO/BBOB platform](https://github.com/numbbo/coco) for new
   work. See [Reusing this repository](#reusing-this-repository) below.
3. **Langdon and Poli instances**, from W.B. Langdon and R. Poli, ["Evolving
   problems to learn about Particle Swarm Optimizers and other search
   algorithms"](https://doi.org/10.1109/TEVC.2006.886448), IEEE Trans. Evol.
   Comput. 11(5) 561-578, 2007, through the function `matlab/langdonpoli.m`.
4. **Clustering-based instances**, following M. Gallagher, ["Towards
   improved benchmarking of black-box optimization algorithms using
   clustering problems"](https://doi.org/10.1007/s00500-016-2094-1), Soft
   Comput. 20(10) 3835-3849, 2016, through the function
   `matlab/clustergallagher.m`, evaluated over the clustering datasets in
   this repository (see [Datasets](#datasets) below).

Sources 1, 3, and 4 above each have a Python equivalent, see
[Usage](#usage) below. Source 2, the vendored BBOB v13.09 platform, is
not ported; see [Reusing this repository](#reusing-this-repository).

## Contents

The repository is organized by platform. MATLAB and Python code each
read the same data files from the shared `data/` directory, so there is
one copy of each dataset.

```
EVOBBO_Instances/
├── data/                    # shared data, read by both platforms below
│   ├── munozsmithmiles.mat  # instance definitions for munozsmithmiles
│   ├── *.mat                 # clustering datasets (see Datasets below)
│   ├── *.csv                 # CSV mirror of every file above, same name
│   └── export_to_csv.py      # regenerates the CSV mirrors from the .mat files
├── matlab/
│   ├── munozsmithmiles.m    # generated BBO instances (see source 1 above)
│   ├── langdonpoli.m         # Langdon and Poli instances (source 3 above)
│   ├── clustergallagher.m    # clustering-based instances (source 4 above)
│   ├── square.m, negexp.m    # helper functions used by munozsmithmiles.m
│   ├── tests/                # matlab.unittest suite, run in CI (below)
│   └── bbob.v13.09/          # reference COCO/BBOB v13.09 platform
│                              # (own Simplified BSD license, see below)
├── python/
│   ├── evobbo_instances/     # Python port of the 3 functions above
│   ├── tests/                # pytest suite, checked against tests/fixtures/
│   └── pyproject.toml, requirements.txt
├── tests/                   # fixtures shared by both test suites above
│   ├── fixtureInputs.m      # candidate solutions both suites evaluate
│   ├── generate_fixtures.m  # (re)writes fixtures/*.csv from fixtureInputs.m
│   └── fixtures/*.csv       # committed MATLAB reference output
├── LICENSE                  # MIT license for this repository's own code
│                             # (matlab/bbob.v13.09/ is vendored under its
│                             # own license, matlab/bbob.v13.09/LICENSE.txt)
└── .github/
    ├── workflows/matlab-tests.yml  # runs matlab/tests/ on push/PR
    └── ISSUE_TEMPLATE/             # bug report and feature request templates
```

## Installation

### MATLAB

The MATLAB code needs a current version of
[MATLAB](https://www.mathworks.com). It has been tested on r2018b, and
should work on earlier versions too. Most functions are vectorized, so
they run fast under MATLAB. No toolbox beyond base MATLAB is required.
Add `matlab/` to the MATLAB path before calling any function:

```matlab
addpath('matlab');
```

To run the MATLAB test suite locally: `run('matlab/tests/run_tests.m')` from
the repository root, or any directory (it resolves its own paths).
[GitHub Actions](.github/workflows/matlab-tests.yml) runs the same suite
on every push and pull request, against real MATLAB.

### Python

The Python port needs Python 3.9 or later. From the `python/` directory:

```bash
cd python
pip install -e .
```

This installs the `evobbo_instances` package and its two dependencies,
`numpy` and `scipy`. Run `pip install -e ".[test]"` instead to also get
`pytest`, and run the test suite with `pytest tests/` (still from
`python/`).

## Usage

Each function takes a matrix of candidate solutions `X` and returns a
vector of fitness values `Y`. Full argument details are in the MATLAB
header comment or the Python docstring of each function.

### Generated instances (`matlab/munozsmithmiles.m` / `python/evobbo_instances/munozsmithmiles.py`)

```matlab
% X is a (d x N) matrix of candidate solutions.
% sid: strategy id (1-3). d: dimension (2 or 10). fid: function id.
Y = munozsmithmiles(X, sid, d, fid);
```

```python
from evobbo_instances import munozsmithmiles
Y = munozsmithmiles(X, sid, d, fid)  # X: numpy array, shape (d, N)
```

The valid range of `fid` depends on `sid` and `d`:

| Strategy / dimension | Max `fid` |
|---|---|
| `s1d2`  | 600 |
| `s1d10` | 120 |
| `s2d2`  | 100 |
| `s2d10` | 500 |
| `s3d2`  | 100 |
| `s3d10` | 100 |

3 individuals (`s2d10` `fid` 2, 41, and 54) carry no expression. Both the
MATLAB and Python functions raise a clear error for these, rather than
returning a silently wrong value.

This function needs `data/munozsmithmiles.mat`. Both the MATLAB and
Python functions find it there automatically, relative to their own
location; pass `data_dir` to the Python function to point somewhere
else instead.

### Langdon and Poli instances (`matlab/langdonpoli.m` / `python/evobbo_instances/langdonpoli.py`)

```matlab
% X is a (d x N) matrix of candidate solutions in [-5, 5]^2.
% fid: function id, 1-19.
Y = langdonpoli(X, fid);
```

```python
from evobbo_instances import langdonpoli
Y = langdonpoli(X, fid)  # X: numpy array, shape (2, N)
```

### Clustering-based instances (`matlab/clustergallagher.m` / `python/evobbo_instances/clustergallagher.py`)

```matlab
% X is a (k*p x N) matrix of candidate solutions, where each column
% holds the positions of k cluster centers in a dataset of
% dimensionality p.
% dataset is an (n x p) matrix, the same orientation as the `data`
% variable stored in each .mat file listed in Datasets below. Pass it
% as loaded, do not transpose it.
load('data/iris.mat');      % loads variable `data`, shape (150 x 4)
Y = clustergallagher(X, data);
```

```python
from evobbo_instances import clustergallagher
from scipy.io import loadmat
data = loadmat('data/iris.mat')['data']  # shape (150, 4) = (n, p)
Y = clustergallagher(X, data)            # dataset: shape (n, p), as loaded
```

`clustergallagher`'s `dataset` argument changed orientation in 2026 (from
`(p, n)` to `(n, p)`, removing the transpose callers used to need). A
caller still transposing before calling now gets a clear error in the
common case, since `dataset`'s swapped shape almost never divides `X`'s
row count evenly; see `matlab/clustergallagher.m`'s version history.

## Datasets

Each `.mat` file below, in `data/` (all files except
`munozsmithmiles.mat`), stores one variable, `data`, of shape (n points
x p features), for use as the `dataset` input to `clustergallagher`.
Each also has a CSV mirror of the same name (for example
`data/iris.csv` next to `data/iris.mat`): plain numbers, no header row,
same `(n, p)` orientation, readable by anything that reads CSV. Both
formats hold the same values; regenerate the CSVs from the `.mat` files
with `python data/export_to_csv.py` if the `.mat` files ever change.

| File | Points (n) | Features (p) |
|---|---|---|
| `data/abalone.mat` | 4177 | 7 |
| `data/balance_scale.mat` | 625 | 4 |
| `data/banknote_authentication.mat` | 1372 | 4 |
| `data/blood_transfusion.mat` | 748 | 4 |
| `data/ecoli.mat` | 336 | 7 |
| `data/energy_efficiency.mat` | 768 | 8 |
| `data/german_towns.mat` | 89 | 3 |
| `data/habermans_survival.mat` | 306 | 3 |
| `data/instanbul_stock_exchange.mat` | 536 | 9 |
| `data/iris.mat` | 150 | 4 |
| `data/pima_indians_diabetes.mat` | 768 | 8 |
| `data/ruspini.mat` | 75 | 2 |
| `data/seeds.mat` | 221 | 7 |
| `data/shuttle_test.mat` | 14500 | 8 |
| `data/shuttle_train.mat` | 43500 | 8 |
| `data/skin.mat` | 245057 | 3 |
| `data/stone_flakes.mat` | 79 | 8 |
| `data/user_knowledge_modeling_test.mat` | 145 | 5 |
| `data/user_knowledge_modeling_train.mat` | 258 | 5 |
| `data/vertebral_column_2C.mat` | 310 | 6 |
| `data/vertebral_column_3C.mat` | 310 | 6 |
| `data/wholesale_customers data.mat` | 440 | 6 |
| `data/yeast.mat` | 1484 | 8 |

These datasets come from public sources such as the UCI Machine Learning
Repository. They are redistributed here only as fixed inputs for
`clustergallagher`.

## Reusing this repository

- **The repository is organized by platform**, so each language's code
  and packaging live together: `matlab/` (MATLAB, plus the vendored
  `bbob.v13.09/`) and `python/` (the `evobbo_instances` package and its
  tests). `data/` holds the `.mat` files both platforms read, so there
  is a single copy of the data.
- **A Python port of the three instance-generating functions**
  (`matlab/munozsmithmiles.m`, `matlab/langdonpoli.m`,
  `matlab/clustergallagher.m`) ships in `python/evobbo_instances/`, see
  [Usage](#usage) above. Its output is checked in `python/tests/` against
  the same reference values in `tests/fixtures/` that `matlab/tests/`
  checks the MATLAB source against, on every CI run, on real MATLAB. See
  [`PYTHON_PORT.md`](PYTHON_PORT.md) for how those reference values were
  produced and what the port does and does not cover.
- **Data files load in Python with no conversion.** Every `.mat` file in
  `data/` is a MATLAB v5 file. Read it with
  `scipy.io.loadmat('data/iris.mat')['data']`. For a tool or language
  without a MATLAB reader at all, read the CSV mirror instead
  (`data/iris.csv`): same values, no dependency beyond a CSV reader.
  `data/munozsmithmiles.csv` mirrors `munozsmithmiles.mat` too, as a
  single long-format table (`sid, d, fid, expression`) instead of six
  cell arrays: it is not yet wired into either loader, so it is a
  human-readable, greppable view of the same 1520 expressions, not
  (yet) an alternative way to call `munozsmithmiles`.
- **`matlab/bbob.v13.09/` is a frozen 2011 snapshot** of the COCO
  benchmarking platform, kept here only as a historical reference for
  the paper, and is not ported. New work should use the [current
  COCO/BBOB platform](https://github.com/numbbo/coco), which ships an
  official Python interface.

## Reproducibility

The instances and datasets in this repository are static outputs, fixed
at publication time. There are no random seeds to set at run time.

## Citation

If you use this repository, cite the paper that matches the instance
source you use (see [Contents](#contents) above), and this repository
itself:

```bibtex
@article{MunozSmithMiles2019,
  author  = {Mu\~{n}oz, M. A. and Smith-Miles, K.},
  title   = {Generating New Space-Filling Test Instances for
             Continuous Black-Box Optimization},
  journal = {Evolutionary Computation},
  year    = {2019},
  doi     = {10.1162/evco_a_00262}
}

@article{LangdonPoli2007,
  author  = {Langdon, W. B. and Poli, R.},
  title   = {Evolving Problems to Learn about Particle Swarm Optimizers
             and Other Search Algorithms},
  journal = {IEEE Transactions on Evolutionary Computation},
  volume  = {11},
  number  = {5},
  pages   = {561--578},
  year    = {2007},
  doi     = {10.1109/TEVC.2006.886448}
}

@article{Gallagher2016,
  author  = {Gallagher, M.},
  title   = {Towards Improved Benchmarking of Black-Box Optimization
             Algorithms Using Clustering Problems},
  journal = {Soft Computing},
  volume  = {20},
  number  = {10},
  pages   = {3835--3849},
  year    = {2016},
  doi     = {10.1007/s00500-016-2094-1}
}
```

See also [`CITATION.cff`](CITATION.cff) for a citation of this repository
in standard machine-readable form.

## Contact

For suggestions, ideas, or problems, use the [issue
tracker](https://github.com/andremun/EVOBBO_Instances/issues), or contact
us through MATILDA's [Queries and Feedback](http://matilda.unimelb.edu.au/contact-us)
page.

## Acknowledgements

Funding for the development of this code was provided by the Australian
Research Council through the Australian Laureate Fellowship FL140100012.
