.. _plugin_structure-section:

Plugins Structure
=================

As mentioned in :ref:`quick-start-section`, the |sdk| package has some utilities to help in the process of creating
a plugin file.

First, to create the plugin use :program:`new`:

.. code-block:: bash

   >>> alfasim-sdk new --help

.. _alfasim_sdk_cli_new_section:

.. click:: alfasim_sdk._internal.cli:new
    :prog: alfasim-sdk new
    :show-nested:

Pyinvoke tasks
--------------

Once the plugin structure is created, you can perform all necessary activities using ``pyinvoke`` tasks, with ``compile``, ``package``  and ``update`` beeing the
most commonly used during plugin development. Below you can find a list of all available along with their descriptions.

.. invoke::
   :module: alfasim_sdk.default_tasks
   :prog: invoke

You can check their implementations `here <https://github.com/ESSS/alfasim-sdk/blob/master/src/alfasim_sdk/default_tasks.py>`_
and you can also overwrite them by just defining a function with the same name of the default task with the ``@sdk_task`` decorator.

For instance, if you want to overwrite the ``clean`` task, define the following inside your ``tasks.py`` in the root of your plugin.

.. code-block:: python

    from invoke import task

    @sdk_task
    def clean():
        print("Overwriting the clean task")
