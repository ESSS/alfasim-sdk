.. _user_interface_hooks-section:

Application Hooks
====================

The application hooks allow plugins to add custom models or custom checks in the application.
To add an application hook it is necessary to implement the given hook in a python file that is
already available on your plugin project folder.

As an example, if the ``alfasim-sdk template`` command was created with the name ``myplugin``, the necessary file to
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
