"""Python port of munozsmithmiles.m.

Functions generated for the paper "Generating New Space-Filling Test
Instances for Continuous Black-Box Optimization", Evol. Comput., 2019.

Each instance is stored in munozsmithmiles.mat as a MATLAB expression
string. This module parses that grammar directly (see _expr.py) instead
of calling MATLAB's eval/feval, which the original .m file used, and
which needed two bug fixes there (see munozsmithmiles.m's version
history) plus two extra helper functions (square.m, negexp.m) to run at
all. Validated against MATLAB reference output in
tests/test_munozsmithmiles.py.
"""

from pathlib import Path

import numpy as np
from scipy.io import loadmat

from ._expr import ExpressionError, evaluate_expression
from ._paths import DEFAULT_DATA_DIR

_VALID_SID = (1, 2, 3)
_VALID_D = (2, 10)

# Cache of loaded expression lists, keyed by (data_dir, sid, d), so
# repeated calls do not re-read the .mat file. Unlike the MATLAB
# source's cache (fixed in this port's companion .m file), this cache
# keys on every input that changes which expressions are loaded, so it
# is always correct to switch sid, d, or data_dir between calls.
_CACHE = {}


def _load_expressions(sid, d, data_dir):
    key = (str(data_dir), sid, d)
    if key not in _CACHE:
        if sid not in _VALID_SID or d not in _VALID_D:
            raise ValueError(
                "Either the strategy number or the dimension are incorrect. "
                "Choose a strategy number between 1 and 3 and a dimension "
                "equal to 2 or 10."
            )
        var_name = f"s{sid}d{d}"
        mat_path = Path(data_dir) / "munozsmithmiles.mat"
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
        data_dir: directory containing munozsmithmiles.mat. Defaults to
            the repository's data/ directory.

    Returns:
        A numpy array of shape (N,) with one fitness value per column
        of X.

    Raises:
        ValueError: if sid, d, or fid is out of range.
        ExpressionError: if the requested individual has no expression
            (a small number of individuals, all in s2d10, are empty).
    """
    if data_dir is None:
        data_dir = DEFAULT_DATA_DIR
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] != d:
        raise ValueError(f"X must have shape ({d}, N) to match d={d}, got {X.shape}")

    exprs = _load_expressions(sid, d, data_dir)
    nfunc = len(exprs)
    if not (1 <= fid <= nfunc):
        raise ValueError(
            f"The function index {fid} is incorrect, there are {nfunc} "
            f"functions in experiment s{sid}d{d}"
        )

    expr = exprs[fid - 1]
    try:
        return evaluate_expression(expr, X)
    except ExpressionError as exc:
        raise ExpressionError(
            f"Function {fid} in experiment s{sid}d{d} has no expression "
            f"(empty individual): {exc}"
        ) from exc
