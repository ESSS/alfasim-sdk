ALFAsim-SDK
===========

The |sdk| help developers to create plugins for |alfasim| application.
Plugins can extend the |alfasim| capabilities in a lot of ways, from adding a simple input to a custom calculation of solver equations.

Some examples of the capabilities that can be extended are:

  * Creation of user-defined GUI models, allowing custom models to be available over the Tree and in the Model Explorer.
  * Registration of additional variables that are not nonlinear system's unknowns, for the |alfasim| solver. Also called "secondary variables"
  * Customization of the hydrodynamic models, supporting the additions of custom Phases/Fields/Layers.
  * Support for inclusion of custom mass, momentum and energy equations.
  * Support for calculating source terms to solver equations.
  * Support for calculating/updating plugin-registered Simulation Variables

For a list of all capabilities that can be expanded check the :ref:`api-reference-section` in the documentation.

Anyone with programming skills can create a Plugin for |alfasim|.  To make it possible, |sdk| provides hooks to customize
the solver and the user interface. To customize the solver, an API in `C` is provided for application
written in C/C++, while, for user interface customization, an API in Python allows the developer to customize
the interface in a declarative way.


To get quick and running with |sdk| you can read the :ref:`quick-start-section` and the
:ref:`plugin-by-example-section` sections

.. toctree::
    :maxdepth: 2
    :glob:

    01_quick_start
    02_alfasim_sdk_by_example

After reading the quick start section and the plugin by example section,
check out these additional resources to help better understand the plugins infrastructure:

.. toctree::
    :maxdepth: 2
    :glob:

    03_plugin_structure
    04_application_hooks
    05_solver_config_hooks
    06_solver_hooks

Dig deeper into specific topics:

.. toctree::
    :maxdepth: 2
    :glob:

    07_workflow
    99_0_reference
