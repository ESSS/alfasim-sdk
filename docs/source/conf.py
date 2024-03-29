# -*- coding: utf-8 -*-
import os
import subprocess
from pathlib import Path

# -- Breathe Configs for ReadTheDocs ------------------------------------------
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

if on_rtd:
    subprocess.run("cd ..; doxygen alfasim_sdk_api.cfg", shell=True)

breathe_projects = {"alfasim_sdk_api": Path("../alfasim_sdk_api/xml")}

# -- Breathe Configs  -------------------------------------------------------

breathe_default_project = "alfasim_sdk_api"

alfasim_sdk_api_project_folder = (
    Path(os.getcwd()).parents[1] / "src/alfasim_sdk/alfasim_sdk_api"
)
breathe_projects_source = {
    "alfasim_sdk_api": (
        alfasim_sdk_api_project_folder,
        ["common.h", "api.h", "detail/bootstrap_win.h"],
    )
}
breathe_doxygen_config_options = {
    "MACRO_EXPANSION": "YES",
    "EXPAND_ONLY_PREDEF": "YES",
    "PREDEFINED": "DLL_EXPORT= DOXYGEN_SHOULD_SKIP_THIS",
}

# -- Project information -----------------------------------------------------

project = ""
copyright = "2019, ESSS"
author = "ESSS"
version = ""
release = ""

# -- Options for Graphviz -------------------------------------------------

graphviz_dot = "dot"
graphviz_dot_args = ["-Tsvg"]
graphviz_output_format = "svg"

# -- General configuration ---------------------------------------------------

extensions = [
    "breathe",
    "sphinx.ext.autodoc",
    "sphinx_click.ext",
    "sphinxinvoke.ext",
    "sphinx.ext.graphviz",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_inline_tabs",
    "sphinx_copybutton",
    "sphinx_togglebutton",
]
add_module_names = False
templates_path = ["_templates"]
source_suffix = ".rst"

master_doc = "index"


rst_prolog = """
.. |alfasim| replace:: :program:`ALFAsim`
.. |sdk| replace:: :program:`ALFAsim-SDK`

.. |new-command| replace:: :ref:`New Command <alfasim_sdk_cli_new_section>`
.. |gui_hook| replace:: :py:func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_get_data_model_type`
.. |container| replace:: :py:func:`~alfasim_sdk.container_model`
.. |model| replace:: :py:func:`~alfasim_sdk.data_model`
.. |s_variable| replace:: :py:func:`~alfasim_sdk.SecondaryVariable`
.. |s_variable_hook| replace:: :py:func:`~alfasim_sdk._internal.hook_specs_gui.alfasim_get_additional_variables`

.. |marker_1| image:: /_static/images/marker_1.png
    :scale: 80%

.. |marker_2| image:: /_static/images/marker_2.png
    :scale: 80%

.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

.. |tracer_warning_text| replace::
    This is advanced customization. We strongly encourage the plugin developer to read the Tracers chapter of
    |alfasim|'s Technical Report available on the `Help` menu at |alfasim| application.

.. |manual| image:: /_static/images/help_menu_technical_manual.png
        :scale: 80%

.. |tracer_warn| replace::
    |tracer_warning_text| |br|
    |manual|

"""

language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "breathe/*"]

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_logo = "_static/images/logo-alfasim.svg"

html_theme_options = {
    "github_url": "https://github.com/esss/alfasim-sdk",
}
html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]
html_favicon = "_static/images/alfasim_gui.ico"

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping = {
    "python": ("http://docs.python.org/3", None),
    "barril": ("https://barril.readthedocs.io/en/latest/", None),
}

# -- Options for Autodoc -----------------------------------------------------

autodoc_typehints = "none"
autodoc_member_order = "groupwise"

# -- Nitpicky config ---------------------------------------------------------

nitpicky = True
nitpick_ignore = [
    ("py:class", "type"),
    ("py:class", "barril.curve.curve.Curve"),  # Barril doesn't have Curve documented.
    ("py:class", "Path"),
    ("py:exc", "FrozenInstanceError"),
    ("cpp:identifier", "ALFAsimSDK_API"),  # Must be checked.
    ("py:class", "void*"),
    ("py:class", "double*"),
    ("py:class", "int*"),
]
