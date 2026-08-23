"""Export every .mat file in this directory to a CSV mirror.

Run from anywhere: python data/export_to_csv.py. Regenerate after any
change to the .mat files (there should not normally be one; they are
the published, static instances and datasets this repository exists to
distribute).

Two kinds of export, matching the two kinds of .mat file in this
directory:

- Each numeric dataset .mat file (all of them except
  munozsmithmiles.mat) has one variable, `data`, a plain (n, p) matrix.
  Its CSV mirror has the same name and holds that matrix directly, no
  header row, one row per data point, matching data's own orientation.
- munozsmithmiles.mat stores six cell arrays of GP expression strings
  (s1d2, s1d10, s2d2, s2d10, s3d2, s3d10), keyed by strategy id and
  dimension. Its CSV mirror, munozsmithmiles.csv, is a single long-format
  table with columns sid, d, fid, expression: one row per stored
  individual, 1520 rows total (including the 3 with an empty
  expression, see munozsmithmiles.m's version history), fid numbered
  1-based to match the MATLAB and Python function signatures.

Neither export changes the data: this is an additional, cross-platform
representation of what the .mat files already hold, not a replacement
for them (see README.md's Reusing this repository section for why both
formats stay).

By: Mario Andres Munoz Acosta
    School of Mathematics and Statistics
    The University of Melbourne
    Australia
    2026
"""

import csv
from pathlib import Path

import numpy as np
from scipy.io import loadmat

DATA_DIR = Path(__file__).resolve().parent

_STRATEGIES = (1, 2, 3)
_DIMENSIONS = (2, 10)


def _format_value(value, is_integer_dtype):
    if is_integer_dtype:
        return str(int(value))
    # repr() of a Python float is the shortest decimal string that
    # round-trips back to the exact same float64 value.
    return repr(float(value))


def export_dataset(mat_path):
    csv_path = mat_path.with_suffix(".csv")
    data = loadmat(mat_path)["data"]
    is_integer_dtype = np.issubdtype(data.dtype, np.integer)
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        for row in data:
            writer.writerow(_format_value(v, is_integer_dtype) for v in row)
    return csv_path


def export_munozsmithmiles(mat_path):
    csv_path = mat_path.with_suffix(".csv")
    var_names = [f"s{sid}d{d}" for sid in _STRATEGIES for d in _DIMENSIONS]
    mat = loadmat(mat_path, variable_names=var_names, squeeze_me=True)
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["sid", "d", "fid", "expression"])
        for sid in _STRATEGIES:
            for d in _DIMENSIONS:
                exprs = np.atleast_1d(mat[f"s{sid}d{d}"])
                for fid, expr in enumerate(exprs, start=1):
                    text = expr.decode() if isinstance(expr, bytes) else str(expr)
                    if text.strip() == "[]":
                        text = ""  # empty individual, see munozsmithmiles.m
                    writer.writerow([sid, d, fid, text])
    return csv_path


def main():
    written = []
    for mat_path in sorted(DATA_DIR.glob("*.mat")):
        if mat_path.stem == "munozsmithmiles":
            written.append(export_munozsmithmiles(mat_path))
        else:
            written.append(export_dataset(mat_path))
    for path in written:
        print(f"Wrote {path.relative_to(DATA_DIR.parent)}")


if __name__ == "__main__":
    main()
