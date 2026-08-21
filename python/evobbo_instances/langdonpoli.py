"""Python port of langdonpoli.m.

Functions from Langdon and Poli 2007 (IEEE Trans. Evol. Comput.), generated
for the paper "Generating New Space-Filling Test Instances for Continuous
Black-Box Optimization", Evol. Comput., 2019.

To make these functions' range, which is [-10, 10]^2, compatible with the
range defined in the BBOB benchmark set, which is [-5, 5]^2, X is
multiplied by 2, and Y is made zero if X exceeds the bounds.

Ported line-by-line from the MATLAB source. Validated against MATLAB
reference output in tests/test_langdonpoli.py.
"""

import numpy as np

# One function per fid (1-19 in the MATLAB source, 0-18 here). Each
# operates on X of shape (2, N): row 0 is the first dimension, row 1 is
# the second.
_FUNCTIONS = [
    lambda x: 0.11 + 0.77 * x[0] * (1 - x[0]) - 0.075 * x[1],  # Fig 2
    lambda x: 0.127 + 0.063 * x[0],  # Fig 3
    lambda x: x[1] * (1.32 + 1.78 * x[0] - x[0] ** 2 - x[1]) + 0.37,  # Fig 4
    lambda x: 0.54 * x[0] - x[0] ** 2 + 0.24 * x[1] - 1.26,  # Fig 5
    lambda x: 0.063 * x[0] - 0.052,  # Fig 6
    lambda x: -(0.171 + 0.0188 * x[1]) * x[1],  # Fig 7
    lambda x: 0.00124 * (x[0] ** 2) * x[1],  # Fig 12
    lambda x: x[0] * (0.643 + x[1] - x[0] * (0.299 * x[0] + 2.81 + x[1] + x[1] ** 2)),  # Fig 13
    lambda x: (1.27 - 1.1 * x[0] - 0.53 * x[0] ** 2) * x[0],  # Fig 20
    lambda x: (0.33 - 0.32 * x[0] - 2.32 * x[1]) * x[1],  # Fig 21
    lambda x: x[1] * (0.093 + 0.39 * x[1] + 0.15 * x[1] ** 2 - 0.17 * x[1] ** 3
                       - (0.19 * x[1] ** 2 + 0.20 * x[1] ** 3) * x[0] ** 2),  # Fig 22
    lambda x: x[0] - (x[0] - 1) / x[0],  # Fig 23
    lambda x: 0.063 * x[0],  # Fig 24
    lambda x: -(0.13 + 0.24 * x[1]) * x[1],  # Fig 25
    lambda x: 0.0043 + 0.024 * x[1],  # Fig 28
    lambda x: 0.102 + 0.00189 * x[1] + 0.00635 * x[1] ** 2,  # Fig 29
    lambda x: x[0] - x[1],  # Fig 32
    lambda x: (1.03 + 2.81 * x[0]) * x[1],  # Fig 33
    lambda x: (x[0] ** 2) * (x[1] ** 4),  # Fig 34
]


def langdonpoli(X, fid):
    """Evaluate one Langdon and Poli (2007) test function.

    Args:
        X: array_like of shape (2, N), candidate solutions.
        fid: function id, an integer from 1 to 19 (matches the MATLAB
            source's 1-based numbering).

    Returns:
        A numpy array of shape (N,) with one fitness value per column
        of X.
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] != 2:
        raise ValueError(f"X must have shape (2, N), got {X.shape}")
    if not (1 <= fid <= len(_FUNCTIONS)):
        raise ValueError(
            f"The function index {fid} is incorrect, there are "
            f"{len(_FUNCTIONS)} functions available"
        )

    X = 2.0 * X
    Y = _FUNCTIONS[fid - 1](X)
    Y = np.where(np.any(np.abs(X) > 10, axis=0), 0.0, Y)
    return Y
