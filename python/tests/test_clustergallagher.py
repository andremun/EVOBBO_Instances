"""Validate clustergallagher against fixed MATLAB (Octave) reference output.

See tests/generate_fixtures.m for how tests/fixtures/clustergallagher.csv
was produced.
"""

import csv
from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from evobbo_instances import clustergallagher
from evobbo_instances._paths import DEFAULT_DATA_DIR

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"

# Same fixed input as tests/generate_fixtures.m: 2 candidates, k=3
# clusters, p=4 (iris has 4 features).
X = np.array(
    [
        [0.10, 0.55],
        [0.20, -0.10],
        [-0.30, 0.40],
        [0.15, 0.05],
        [0.40, -0.20],
        [-0.10, 0.30],
        [0.05, 0.15],
        [-0.25, -0.35],
        [0.30, 0.10],
        [0.00, -0.15],
        [-0.20, 0.25],
        [0.10, 0.20],
    ]
)


def _load_fixture():
    with open(FIXTURES_DIR / "clustergallagher.csv", newline="") as f:
        return [(int(row["sample"]), float(row["y"])) for row in csv.DictReader(f)]


def _iris_dataset():
    return loadmat(DEFAULT_DATA_DIR / "iris.mat")["data"]  # (150, 4) = (n, p), native orientation


@pytest.mark.parametrize("sample,expected", _load_fixture())
def test_matches_matlab_reference(sample, expected):
    Y = clustergallagher(X, _iris_dataset())
    assert Y[sample - 1] == pytest.approx(expected, rel=1e-9)


def test_mismatched_dimensionality_raises():
    with pytest.raises(ValueError):
        clustergallagher(X[:-1, :], _iris_dataset())  # 11 rows, not a multiple of p=4


def test_transposed_dataset_warns():
    # A dataset with more columns than rows is unusual for these
    # benchmark datasets and is exactly what an accidental transpose
    # looks like. Built synthetically (2 points, 12 features, k=1) so
    # the kp % p guard does not also raise and mask the warning.
    synthetic_dataset = np.ones((2, 12))
    synthetic_X = np.ones((12, 1))
    with pytest.warns(UserWarning, match="more columns"):
        clustergallagher(synthetic_X, synthetic_dataset)
