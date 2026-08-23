"""Python port of clustergallagher.m.

Fitness function following M. Gallagher, "Towards improved benchmarking
of black-box optimization algorithms using clustering problems", Soft
Comput. 20(10) 3835-3849, 2016.

Ported from the MATLAB source, replacing the embedded L2_distance helper
(there credited to Roland Bunschoten and Laurens van der Maaten) with the
equivalent scipy.spatial.distance.cdist. Like the MATLAB source, this
loops over the N candidate solutions one at a time rather than
vectorizing across all of them: clustergallagher.m's own version history
notes that an earlier, fully vectorized version (arrayfun over N) was
deliberately replaced with this per-candidate loop for speed and memory
reasons, since a full N-way vectorization would need one (k, n) distance
matrix per candidate held in memory at once. The per-candidate distance
computation itself is vectorized, through cdist. Validated against
MATLAB reference output in tests/test_clustergallagher.py.
"""

import warnings

import numpy as np
from scipy.spatial.distance import cdist


def clustergallagher(X, dataset):
    """Evaluate the Gallagher (2016) clustering fitness function.

    Args:
        X: array_like of shape (k*p, N). Each column holds the
            positions of k cluster centers of dimensionality p, so the
            dimensionality of the optimization problem is k*p.
        dataset: array_like of shape (n, p), n data points of
            dimensionality p to cluster: one row per point, the same
            orientation the `data` array already has in this
            repository's .mat files. Do not transpose it before
            passing it here.

    Returns:
        A numpy array of shape (N,) with one fitness value per column
        of X: the sum, over all n data points, of the squared distance
        to the nearest of the k cluster centers.

    Note:
        Before this version, `dataset` was (p, n) and callers
        transposed the native (n, p) `data` array by hand. A caller
        still doing that transpose now likely hits the ValueError
        below (kp not a multiple of the wrong, swapped p), rather than
        silently getting a wrong result.
    """
    X = np.asarray(X, dtype=float)
    dataset = np.asarray(dataset, dtype=float)
    if dataset.ndim != 2:
        raise ValueError(f"dataset must have shape (n, p), got {dataset.shape}")
    n, p = dataset.shape
    if p > n:
        warnings.warn(
            f"dataset has more columns ({p}) than rows ({n}). dataset should be "
            "(n, p): one row per data point. If you transposed it before calling, "
            "pass it untransposed instead.",
            stacklevel=2,
        )
    if X.ndim != 2:
        raise ValueError(f"X must have shape (k*p, N), got {X.shape}")
    kp, N = X.shape
    if kp % p != 0:
        raise ValueError(
            f"X has {kp} rows, which is not a multiple of the dataset "
            f"dimensionality p={p}"
        )
    k = kp // p

    Y = np.empty(N)
    for i in range(N):
        centers = X[:, i].reshape(k, p)  # one cluster center per row
        distances = cdist(centers, dataset)  # (k, n)
        nearest = np.min(distances, axis=0)  # (n,)
        Y[i] = np.sum(nearest ** 2)
    return Y
