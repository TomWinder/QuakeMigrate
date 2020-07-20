# -*- coding: utf-8 -*-
"""
The :mod:`quakemigrate.pick` module handles the picking of seismic phases. The
default method makes the phase picks by fitting a 1-D Gaussian to the Onset
function.

Feel free to contribute more phase picking methods!

:copyright:
    2020, QuakeMigrate developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from .gaussianpicker import GaussianPicker  # NOQA
from .pick import PhasePicker  # NOQA
