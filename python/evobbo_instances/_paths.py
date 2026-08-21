"""Shared default data location for the evobbo_instances package."""

from pathlib import Path

# The .mat data files live in data/ at the repository root, shared by
# both the MATLAB functions (in matlab/) and this package (in python/).
# This file is at <repo_root>/python/evobbo_instances/_paths.py, so
# repo_root is two levels up from this file's parent.
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
