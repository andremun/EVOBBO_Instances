"""Python port of the EVOBBO_Instances MATLAB functions.

This package reproduces the three instance-generating functions
distributed as MATLAB files in ``matlab/`` at the root of this
repository: ``munozsmithmiles.m``, ``langdonpoli.m``, and
``clustergallagher.m``. See the repository README for background and
PYTHON_PORT.md for the port's scope and validation approach.

Every function in this package reads its input data from the .mat
files in ``data/`` at the repository root by default. Pass
``data_dir`` to any function to point at a different location, for
example a copy of just the .mat files you need.
"""

from .clustergallagher import clustergallagher
from .langdonpoli import langdonpoli
from .munozsmithmiles import munozsmithmiles

__all__ = ["clustergallagher", "langdonpoli", "munozsmithmiles"]
__version__ = "0.1.0"
