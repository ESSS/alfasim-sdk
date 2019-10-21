# -*- coding: utf-8 -*-
import os
import subprocess
from pathlib import Path

# -- Breathe Configs for ReadTheDocs ------------------------------------------
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

if on_rtd:
    subprocess.run("cd ..; doxygen alfasim_sdk_api.cfg", shell=True)
    breathe_projects = {"alfasim_sdk_api": "../alfasim_sdk_api/xml"}
else:
    breathe_projects = {
        "alfasim_sdk_api": "../_build/breathe/doxygen/alfasim_sdk_api/xml"
    }

# -- Breathe Configs  -------------------------------------------------------

breathe_default_project = "alfasim_sdk_api"

alfasim_sdk_api_project_folder = Path(os.getcwd()).parents[1] / "alfasim_sdk_api"
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
    "sphinx.ext.autodoc",
    "breathe",
    "sphinx_click.ext",
    "sphinx.ext.graphviz",
]

autodoc_typehints = "none"
templates_path = ["_templates"]
source_suffix = ".rst"

master_doc = "index"


rst_prolog = """
.. |alfasim| replace:: :program:`ALFAsim`
.. |sdk| replace:: :program:`ALFAsim-SDK`

.. |template-command| replace:: :ref:`Template Command <alfasim_sdk_cli_template_section>`
.. |gui_hook| replace:: :py:func:`alfasim_get_data_model_type`
.. |container| replace:: :py:func:`alfasim_sdk.models.container_model`
.. |model| replace:: :py:func:`alfasim_sdk.models.data_model`
.. |s_variable| replace:: :py:func:`alfasim_sdk.variables.SecondaryVariable`
.. |s_variable_hook| replace:: :py:func:`alfasim_get_additional_variables`

.. |marker_1| image:: _static/images/marker_1.png
    :scale: 80%

.. |marker_2| image:: _static/images/marker_2.png
    :scale: 80%

.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

.. |tracer_warning_text| replace::
    This is advanced customization. We strongly encourage the plugin developer to read the Tracers chapter of
    |alfasim|'s Technical Report available on the `Help` menu at |alfasim| application.

.. |manual| image:: _static/images/help_menu_technical_manual.png
        :scale: 80%

.. |tracer_warn| replace::
    |tracer_warning_text| |br|
    |manual|

"""

language = None
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "breathe/*"]
pygments_style = "monokai"

# -- Options for HTML output -------------------------------------------------
html_theme = "alabaster"
html_theme_options = {
    "analytics_id": "UA-149094345-1",
    "link": "#3782BE",
    "link_hover": "#3782BE",
    "font_family": '"Avenir Next", Calibri, "PT Sans", sans-serif',
    "head_font_family": '"Avenir Next", Calibri, "PT Sans", sans-serif',
    "font_size": "18px",
    "page_width": "980px",
    "show_relbars": True,
}
html_static_path = ["_static"]
html_sidebars = {"**": ["searchbox.html", "about.html", "fulltoc.html"]}
html_favicon = "_static/images/alfasim_gui.ico"
html_logo = "_static/images/logo-alfasim.svg"
