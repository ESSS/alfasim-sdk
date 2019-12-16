# -*- coding: utf-8 -*-
"""Top-level package for alfasim-sdk."""
import pluggy

__author__ = """ESSS"""
__email__ = "foss@esss.co"
__version__ = "0.2.0"

hookimpl = pluggy.HookimplMarker("ALFAsim")


def get_alfasim_sdk_api_path():
    """
    Return the directory that contains the alfasim_sdk_api with the header files
    """
    from alfasim_sdk import hook_specs
    from pathlib import Path

    return str(Path(hook_specs.__file__).parents[1])
