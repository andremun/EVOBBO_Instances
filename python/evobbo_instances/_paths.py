"""Shared default data location for the evobbo_instances package."""

from pathlib import Path

# The .mat data files live in data/ at the repository root. Both the
# MATLAB functions (in matlab/) and this package (in python/) share
# them. This file is at <repo_root>/python/evobbo_instances/_paths.py,
# so repo_root is two levels up from this file's parent.
#
# This default only resolves to a real directory when the package runs
# from a source checkout of this repository. That means an editable
# install (`pip install -e .`), or the repository root on PYTHONPATH.
# A normal, non-editable install (for example from a built wheel)
# copies only this package into site-packages. It has no sibling
# data/ directory, so DEFAULT_DATA_DIR will not exist. Callers in that
# situation must pass data_dir explicitly. See resolve_data_dir() below
# for the check that turns a missing data directory into a clear error
# instead of a confusing failure inside scipy.io.loadmat.
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def resolve_data_dir(data_dir):
    """Resolve data_dir to a Path. Default to DEFAULT_DATA_DIR.

    Raise FileNotFoundError with a clear message if the directory does
    not exist. This replaces a later, less clear failure inside
    scipy.io.loadmat.
    """
    resolved = Path(DEFAULT_DATA_DIR if data_dir is None else data_dir)
    if not resolved.is_dir():
        raise FileNotFoundError(
            f"Data directory not found: {resolved}. This package needs a "
            "source checkout of this repository, with data/ next to "
            "matlab/ and python/. If that is not available, pass an "
            "explicit data_dir argument. It must point at a directory "
            "that holds the required .mat files."
        )
    return resolved
