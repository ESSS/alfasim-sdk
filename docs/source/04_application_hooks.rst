.. _user_interface_hooks-section:

Application Hooks
====================

The application hooks allows plugins top add custom models or custom checks in application as well to configure internal
setting from the ALFAsim. To add an application hook is necessary to implement the given hook in a python file that is
already available on your plugin project folder.

As an example, if the ``alfasim-sdk template`` command was created with the name ``myplugin`` the necessary file to
be customized will be located on: :menuselection:`myplugin --> src --> python --> myplugin.py`

.. contents::
    :depth: 3
    :local:

.. _alfasim_get_data_model_type:

Plugin Model
------------

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_data_model_type


Status Monitor
--------------


.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_status


Additional Variables
--------------------

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_additional_variables


.. _multi-field-description:

Hydrodynamic Model
-------------------

|alfasim| provides way to customize the hydrodynamic model available within the application, if the usage of
the hook listed bellow, the plugin can:

 - Add new fields
 - Add/update phases
 - Add/update layers

.. note::
    For each new added ``field`` is considered a mass conservation equation and for each new added ``layer`` is considered
    a momentum conservation and an energy conservation equations.

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_configure_fields

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_configure_phases

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_configure_layers

In order to complement the ``Hydrodynamic model`` customization, it's possible to inform to |alfasim| which phases
(added from plugin or not) will have the state variables calculated by plugin.

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_phase_properties_calculated_from_plugin

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_phase_interaction_properties_calculated_from_plugin


.. _get_user_defined_tracer_from_plugin:

User Defined Tracers
--------------------

.. warning::
    |tracer_warn|

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_user_defined_tracers_from_plugin
