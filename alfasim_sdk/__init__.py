# -*- coding: utf-8 -*-
"""Top-level package for alfasim-sdk."""
import pluggy

from alfasim_sdk import _version

__author__ = "ESSS"
__email__ = "foss@esss.co"
__version__ = _version.__version__

from alfasim_sdk.units import register_units

hookimpl = pluggy.HookimplMarker("ALFAsim")

register_units()


def get_alfasim_sdk_api_path():
    """
    Return the directory that contains the alfasim_sdk_api with the header files
    """
    from alfasim_sdk import hook_specs
    from pathlib import Path

    return str(Path(hook_specs.__file__).parents[1])
