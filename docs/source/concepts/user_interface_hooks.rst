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

Customizing the user interface
------------------------------

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_data_model_type


Customizing the status monitor
------------------------------


.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_status


Additional variables
--------------------

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_get_additional_variables



Multi-field description
-----------------------


.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_configure_fields

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_configure_layers

.. autofunction:: alfasim_sdk.hook_specs_gui.alfasim_configure_phases


???
---

.. autofunction::alfasim_sdk.hook_specs_gui.alfasim_get_phase_properties_calculated_from_plugin

.. autofunction::alfasim_sdk.hook_specs_gui.alfasim_get_phase_interaction_properties_calculated_from_plugin

.. autofunction::alfasim_sdk.hook_specs_gui.alfasim_get_user_defined_tracers_from_plugin
