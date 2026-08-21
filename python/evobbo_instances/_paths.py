"""Shared default data location for the evobbo_instances package."""

from pathlib import Path

# The .mat data files live in data/ at the repository root, shared by
# both the MATLAB functions (in matlab/) and this package (in python/).
# This file is at <repo_root>/python/evobbo_instances/_paths.py, so
# repo_root is two levels up from this file's parent.
#
# This default only resolves to a real directory when the package runs
# from a source checkout of this repository (an editable install,
# `pip install -e .`, or the repository root on PYTHONPATH). A normal,
# non-editable install (for example from a built wheel) copies only
# this package into site-packages, with no sibling data/ directory, so
# DEFAULT_DATA_DIR will not exist. Callers in that situation must pass
# data_dir explicitly. See resolve_data_dir() below for the check that
# turns a missing data directory into a clear error instead of a
# confusing failure inside scipy.io.loadmat.
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def resolve_data_dir(data_dir):
    """Resolve data_dir to a Path, defaulting to DEFAULT_DATA_DIR.

    Raises FileNotFoundError with an actionable message if the
    resulting directory does not exist, instead of letting a later
    scipy.io.loadmat call fail with a less clear error.
    """
    resolved = Path(DEFAULT_DATA_DIR if data_dir is None else data_dir)
    if not resolved.is_dir():
        raise FileNotFoundError(
            f"Data directory not found: {resolved}. This package expects "
            "either a source checkout of the EVOBBO_Instances repository "
            "(so data/ sits next to matlab/ and python/), or an explicit "
            "data_dir argument pointing at a directory holding the "
            "required .mat files."
        )
    return resolved
