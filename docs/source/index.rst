ALFASIM-SDK
===========

The ALFAsim-SDK is a tool to help developers to create a new plugin for ALFAsim application.
Plugins are extensions that expands the ALFAsim capabilities, the plugins are a compressed file named `hmplugin`,
that contains all necessary files bundled in a single package, ready to be distributed for other users.
Some examples the capabitilies that can extended are:

  * Creation of user-defined models, allowing custom models to be available over the Tree and in the Model Explorer.
  * Registration of secondary variables, allowing plugins to register new additional variables on ALFAsim.
  * Customization of the hydrodynamic models, supporting the additions of custom Phases/Fields/Layers.
  * Support for calculating source terms to solver equations.
  * Support for calculating/updating plugin-defined Simulation Variables

For a list of all capabilities that can be expanded check the API reference section in the documentation.

Anyone with programming skills can create a Plugin, for that, alfasim-SDK provides an API in `C` that can be easily used by C/C++ programs.
For user interface customization, it's provided as well an API that allows the developers to declare models and their fields.

To get quick and running with ``ALFAsim-SDK`` you can read the :ref:`quick-start-section` section.


.. toctree::
    :maxdepth: 2
    :glob:

    quick_start

After reading the quick start section, check out these additional resources to help better understand the project flow:

.. toctree::
    :maxdepth: 2
    :glob:

    concepts/creating_plugins
    concepts/solver_hooks

Dig deeper into specific topics:

.. toctree::
    :maxdepth: 2
    :glob:

    api/*
