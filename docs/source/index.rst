ALFASIM-SDK
===========

The ALFAsim-SDK help developers to create plugins for an ALFAsim application.
Plugins can extend the ALFAsim capabilities in a lot of ways, from adding a simple input to a custom calculation of solver equations.

Some examples of the capabilities that can be extended are:

  * Creation of user-defined models, allowing custom models to be available over the Tree and in the Model Explorer.
  * Registration of secondary variables, allowing plugins to register new additional variables on ALFAsim.
  * Customization of the hydrodynamic models, supporting the additions of custom Phases/Fields/Layers.
  * Support for calculating source terms to solver equations.
  * Support for calculating/updating plugin-defined Simulation Variables

For a list of all capabilities that can be expanded check the :ref:`api-reference-section` in the documentation.

Anyone with programming skills can create a Plugin for ALFAsim, for that, alfasim-SDK provides hooks to customize
the solver and the user interface. In order to customize the solver, an API in `C` is provided for application
writeen in C/C++, while, for user interface customization, an API in Python allows the developer to customize
the interface in a declarative way.


To get quick and running with ``ALFAsim-SDK`` you can read the :ref:`quick-start-section` and the
:ref:`plugin-by-example-section` sections

.. toctree::
    :maxdepth: 2
    :glob:

    quick_start
    alfasim_sdk_by_example

After reading the quick start section and the plugin by example section,
check out these additional resources to help better understand the plugin workflow:

.. toctree::
    :maxdepth: 2
    :glob:

    concepts/plugin_structure
    concepts/user_interface_hooks
    concepts/solver_hooks

Dig deeper into specific topics:

.. toctree::
    :maxdepth: 2
    :glob:

    api/reference
