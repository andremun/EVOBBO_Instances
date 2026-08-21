"""Validate munozsmithmiles against fixed MATLAB (Octave) reference output.

See tests/generate_fixtures.m for how tests/fixtures/munozsmithmiles.csv
was produced, and munozsmithmiles.m's version history for the two bugs
fixed there (a cache check and a feval/eval mix-up) so this reference
output could be produced at all.
"""

import csv
from pathlib import Path

import numpy as np
import pytest

from evobbo_instances import munozsmithmiles
from evobbo_instances._expr import ExpressionError

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Same fixed inputs as tests/generate_fixtures.m.
X2 = np.array([[-1.0, -0.3, 0.0, 0.4, 1.0], [0.5, -0.4, 0.0, 0.3, -0.6]])
X10 = np.array(
    [
        np.linspace(-1, 1, 5),
        np.linspace(1, -1, 5),
        np.linspace(-0.5, 0.5, 5),
        np.linspace(0.5, -0.5, 5),
        np.linspace(-1, 0, 5),
        np.linspace(0, 1, 5),
        np.linspace(-0.2, 0.2, 5),
        np.linspace(0.2, -0.2, 5),
        np.linspace(-0.8, 0.3, 5),
        np.linspace(0.3, -0.8, 5),
    ]
)
_X_BY_D = {2: X2, 10: X10}


def _load_fixture():
    rows = []
    with open(FIXTURES_DIR / "munozsmithmiles.csv", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                (
                    int(row["sid"]),
                    int(row["d"]),
                    int(row["fid"]),
                    int(row["sample"]),
                    float(row["y"]),
                )
            )
    return rows


@pytest.mark.parametrize("sid,d,fid,sample,expected", _load_fixture())
def test_matches_matlab_reference(sid, d, fid, sample, expected):
    Y = munozsmithmiles(_X_BY_D[d], sid, d, fid)
    assert Y[sample - 1] == pytest.approx(expected, rel=1e-9, abs=1e-9)


def test_empty_individual_raises():
    # s2d10 fid 2, 41, and 54 have no expression (see PYTHON_PORT.md).
    with pytest.raises(ExpressionError):
        munozsmithmiles(X10, 2, 10, 2)


def test_out_of_bounds_fid_raises():
    with pytest.raises(ValueError):
        munozsmithmiles(X2, 1, 2, 10_000)


def test_invalid_strategy_raises():
    with pytest.raises(ValueError):
        munozsmithmiles(X2, 4, 2, 1)


def test_mismatched_dimension_raises():
    with pytest.raises(ValueError):
        munozsmithmiles(X10, 1, 2, 1)  # X10 has 10 rows, d=2 expects 2


def test_missing_data_dir_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        munozsmithmiles(X2, 1, 2, 1, data_dir="/no/such/directory")
