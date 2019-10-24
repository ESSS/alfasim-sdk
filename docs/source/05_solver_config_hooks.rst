.. _solver_config_hooks-section:

Solver Configuration Hooks
==========================

The solver configuration hooks allow plugins to configure internal settings from |alfasim|.
To add a configuration hook it is necessary to implement the given `hook` in a python file that is already available
on your plugin project folder.

As an example, if a plugin was created using ``alfasim-sdk template`` command and named as ``myplugin`` the necessary file to
be customized would be located on: :menuselection:`myplugin --> src --> python --> myplugin.py`

.. contents::
    :depth: 3
    :local:

Additional Variables
--------------------

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_additional_variables

.. _multi-field-description:

Hydrodynamic Model
-------------------

|alfasim| provides a way to customize the hydrodynamic model available within the application, with the usage of
the hook listed below, the plugin can:

 - Add new fields
 - Add/update phases
 - Add/update layers

.. note::
    For each new added ``field`` is considered a mass conservation equation and for each new added ``layer`` is considered
    a momentum conservation and an energy conservation equations, depending on the energy model used at |alfasim|.

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_configure_fields

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_configure_phases

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_configure_layers

In order to complement the ``Hydrodynamic model`` customization, it is possible to inform |alfasim| which phases
(added from plugin or not) will have the state variables calculated by plugin.

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_phase_properties_calculated_from_plugin

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_phase_interaction_properties_calculated_from_plugin


.. _get_user_defined_tracer_from_plugin:

User Defined Tracers
--------------------

.. warning::
    |tracer_warn|

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_user_defined_tracers_from_plugin
