.. _user_interface_hooks-section:

Application Hooks
====================

The application hooks allow plugins to add custom models or custom checks in the application.
To add an application hook it is necessary to implement the given hook in a python file that is
already available on your plugin project folder.

For example, after executing the command ``alfasim-sdk new myplugin``, the file ``myplugin.py``, located at :menuselection:`myplugin --> src --> python` should be customized.

.. contents::
    :depth: 3
    :local:

.. _alfasim_get_data_model_type:

Plugin Model
------------

.. autofunction:: alfasim_sdk._internal.hook_specs_gui.alfasim_get_data_model_type


Status Monitor
--------------

.. autofunction:: alfasim_sdk._internal.hook_specs_gui.alfasim_get_status
