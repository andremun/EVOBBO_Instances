"""Validate langdonpoli against fixed MATLAB (Octave) reference output.

See tests/generate_fixtures.m for how tests/fixtures/langdonpoli.csv was
produced, and PYTHON_PORT.md for the provenance caveat (generated with
GNU Octave, not MathWorks MATLAB).
"""

import csv
from pathlib import Path

import numpy as np
import pytest

from evobbo_instances import langdonpoli

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Same fixed input grid as tests/generate_fixtures.m.
X = np.array(
    [
        [-6.0, -2.5, -1.0, 0.0, 1.0, 2.5, 6.0],
        [3.0, 1.5, -0.5, 0.0, 0.5, -1.5, -3.0],
    ]
)


def _load_fixture():
    rows = []
    with open(FIXTURES_DIR / "langdonpoli.csv", newline="") as f:
        for row in csv.DictReader(f):
            rows.append((int(row["fid"]), int(row["sample"]), float(row["y"])))
    return rows


@pytest.mark.parametrize("fid,sample,expected", _load_fixture())
def test_matches_matlab_reference(fid, sample, expected):
    Y = langdonpoli(X, fid)
    assert Y[sample - 1] == pytest.approx(expected, abs=1e-9)


def test_out_of_bounds_fid_raises():
    with pytest.raises(ValueError):
        langdonpoli(X, 20)


def test_out_of_domain_is_zeroed():
    # 2 * 6.0 = 12.0 > 10, so this sample should be forced to 0.
    Y = langdonpoli(X, 1)
    assert Y[0] == 0.0
