"""Shared default data location for the evobbo_instances package."""

from pathlib import Path

# The .mat data files live at the repository root, alongside the MATLAB
# functions, not inside this package. This keeps a single copy of the
# data shared by both the MATLAB and Python implementations.
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent
