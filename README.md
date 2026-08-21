# Evolved BBO Instances

[![DOI](https://zenodo.org/badge/198110974.svg)](https://zenodo.org/badge/latestdoi/198110974)

This repository holds test instances and datasets for continuous
black-box optimization (BBO) research. It supports the paper M.A. Muñoz
and K. Smith-Miles, ["Generating New Space-Filling Test Instances for
Continuous Black-Box Optimization"](https://doi.org/10.1162/evco_a_00262),
Evol. Comput., 2019.

The repository provides instances from four sources:

1. **Generated instances** from the methodology in the paper above, through
   the function `munozsmithmiles.m` (needs `square.m` and `negexp.m`,
   also in this repository; see that function's version history for two
   bugs fixed in 2026 that made every call fail before the fix).
2. **Reference BBOB instances** from the "Comparing Continuous Optimization"
   benchmarking platform v13.09 (2011), in `bbob.v13.09/`. Use the
   [current COCO/BBOB platform](https://github.com/numbbo/coco) for new
   work. See [Reusing this repository](#reusing-this-repository) below.
3. **Langdon and Poli instances**, from W.B. Langdon and R. Poli, ["Evolving
   problems to learn about Particle Swarm Optimizers and other search
   algorithms"](https://doi.org/10.1109/TEVC.2006.886448), IEEE Trans. Evol.
   Comput. 11(5) 561-578, 2007, through the function `langdonpoli.m`.
4. **Clustering-based instances**, following M. Gallagher, ["Towards
   improved benchmarking of black-box optimization algorithms using
   clustering problems"](https://doi.org/10.1007/s00500-016-2094-1), Soft
   Comput. 20(10) 3835-3849, 2016, through the function `clustergallagher.m`,
   evaluated over the clustering datasets in this repository (see
   [Datasets](#datasets) below).

## Contents

```
EVOBBO_Instances/
├── munozsmithmiles.m       # generated BBO instances (see source 1 above)
├── munozsmithmiles.mat     # instance definitions used by munozsmithmiles.m
├── langdonpoli.m            # Langdon and Poli instances (source 3 above)
├── clustergallagher.m       # clustering-based instances (source 4 above)
├── square.m, negexp.m       # helper functions used by munozsmithmiles.m
├── *.mat                    # clustering datasets used by clustergallagher.m
│                             # (see Datasets below; excludes munozsmithmiles.mat)
├── bbob.v13.09/             # reference COCO/BBOB v13.09 platform (MATLAB)
├── evobbo_instances/        # Python port of the 3 functions above
├── tests/                   # Python test suite, checked against MATLAB
├── pyproject.toml, requirements.txt  # Python packaging
├── LICENSE                  # MIT license for the code in this repository
└── .github/ISSUE_TEMPLATE/  # bug report and feature request templates
```

## Installation

### MATLAB

The MATLAB code needs a current version of
[MATLAB](https://www.mathworks.com). It has been tested on r2018b, and
should work on earlier versions too. Most functions are vectorized, so
they run fast under MATLAB. No toolbox beyond base MATLAB is required.

### Python

The Python port needs Python 3.9 or later. From the repository root:

```bash
pip install -e .
```

This installs the `evobbo_instances` package and its two dependencies,
`numpy` and `scipy`. Run `pip install -e ".[test]"` instead to also get
`pytest`, and run the test suite with `pytest tests/`.

## Usage

Each function takes a matrix of candidate solutions `X` and returns a
vector of fitness values `Y`. Full argument details are in the MATLAB
header comment or the Python docstring of each function.

### Generated instances (`munozsmithmiles.m` / `munozsmithmiles.py`)

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

This function needs `munozsmithmiles.mat` (MATLAB: on the MATLAB path;
Python: in `data_dir`, which defaults to the repository root).

### Langdon and Poli instances (`langdonpoli.m` / `langdonpoli.py`)

```matlab
% X is a (d x N) matrix of candidate solutions in [-5, 5]^2.
% fid: function id, 1-19.
Y = langdonpoli(X, fid);
```

```python
from evobbo_instances import langdonpoli
Y = langdonpoli(X, fid)  # X: numpy array, shape (2, N)
```

### Clustering-based instances (`clustergallagher.m` / `clustergallagher.py`)

```matlab
% X is a (k*p x N) matrix of candidate solutions, where each column
% holds the positions of k cluster centers in a dataset of
% dimensionality p.
% dataset is a (p x n) matrix, transposed from the (n x p) `data`
% variable stored in each .mat file listed in Datasets below.
load('iris.mat');           % loads variable `data`, shape (150 x 4)
Y = clustergallagher(X, data');
```

```python
from evobbo_instances import clustergallagher
from scipy.io import loadmat
data = loadmat('iris.mat')['data']       # shape (150, 4) = (n, p)
Y = clustergallagher(X, data.T)          # dataset: shape (p, n)
```

## Datasets

Each `.mat` file below (all files except `munozsmithmiles.mat`) stores one
variable, `data`, of shape (n points x p features), for use as the
`dataset` input to `clustergallagher.m`.

| File | Points (n) | Features (p) |
|---|---|---|
| `abalone.mat` | 4177 | 7 |
| `balance_scale.mat` | 625 | 4 |
| `banknote_authentication.mat` | 1372 | 4 |
| `blood_transfusion.mat` | 748 | 4 |
| `ecoli.mat` | 336 | 7 |
| `energy_efficiency.mat` | 768 | 8 |
| `german_towns.mat` | 89 | 3 |
| `habermans_survival.mat` | 306 | 3 |
| `instanbul_stock_exchange.mat` | 536 | 9 |
| `iris.mat` | 150 | 4 |
| `pima_indians_diabetes.mat` | 768 | 8 |
| `ruspini.mat` | 75 | 2 |
| `seeds.mat` | 221 | 7 |
| `shuttle_test.mat` | 14500 | 8 |
| `shuttle_train.mat` | 43500 | 8 |
| `skin.mat` | 245057 | 3 |
| `stone_flakes.mat` | 79 | 8 |
| `user_knowledge_modeling_test.mat` | 145 | 5 |
| `user_knowledge_modeling_train.mat` | 258 | 5 |
| `vertebral_column_2C.mat` | 310 | 6 |
| `vertebral_column_3C.mat` | 310 | 6 |
| `wholesale_customers data.mat` | 440 | 6 |
| `yeast.mat` | 1484 | 8 |

These datasets come from public sources such as the UCI Machine Learning
Repository. They are redistributed here only as fixed inputs for
`clustergallagher.m`.

## Reusing this repository

- **A Python port of the three instance-generating functions**
  (`munozsmithmiles.m`, `langdonpoli.m`, `clustergallagher.m`) ships in
  the `evobbo_instances` package, see [Usage](#usage) above. Its output
  is checked against MATLAB reference values in `tests/`; see
  [`PYTHON_PORT.md`](PYTHON_PORT.md) for how those reference values were
  produced and what the port does and does not cover.
- **Data files load in Python with no conversion.** Every `.mat` file
  above is a MATLAB v5 file. Read it with
  `scipy.io.loadmat('iris.mat')['data']`.
- **`bbob.v13.09/` is a frozen 2011 snapshot** of the COCO benchmarking
  platform, kept here only as a historical reference for the paper, and
  is not ported. New work should use the [current COCO/BBOB
  platform](https://github.com/numbbo/coco), which ships an official
  Python interface.

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
