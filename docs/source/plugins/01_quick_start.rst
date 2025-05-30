.. _quick-start-section:

Quick Start
===========

In this section, it is shown how to create a plugin from scratch with the new command provided by |sdk|.
With this template, you can easily customize your application to extend |alfasim| functionality.

This allows you to experience the complete creation of a plugin workflow in a short time.


Set up the environment
----------------------

The |sdk| is a Python package that helps developers in the process to create a Plugin for |alfasim|, to use
this tool it is necessary to have a Python Interpreter with at least version 3.6. For more details on how to install Python `check
the official docs <https://www.python.org/downloads/>`_.

.. note::

    It is recommended to install the |sdk| using the conda package manager. The following commands will create a conda environment with |sdk| installed.

    .. code-block:: bash

        >>> conda create -n sdk_env
        >>> conda activate sdk_env
        >>> python -m pip install alfasim-sdk

    Alternatively, an ``environment.yml`` can be added to your project and ``alfasim-sdk`` can be declared at ``pip`` dependencies.

    For more details, see `Getting started with conda <https://conda.io/projects/conda/en/latest/user-guide/getting-started.html>`_.


|sdk| requires:

 - ``CMake`` at least version 3.5.2
 - ``Ninja`` at least version 1.7.0


The ``alfasim-sdk`` package has a built in command line interface (CLI) that is used to create a new plugin template. You can get the
help on how to use it with the following command

.. code-block:: bash

   >>> alfasim-sdk --help

Creating a Plugin Project
-------------------------

To create a new project, run:

.. code-block:: bash

   >>> alfasim-sdk new

After the execution of the command above, you will be prompted to fill the following options (all required):

.. code-block:: bash

    >>> alfasim-sdk new
    ... -- Plugin Caption: Myplugin
    ... -- Plugin Id: myplugin
    ... -- Author Name: ESSS
    ... -- Author Email: <email>@<server>


:Plugin Caption: The caption to be used across the application to identify the plugin.
:Plugin Id: The name of the plugin to be referenced during the development.
:Author Name: Name of the plugin author to be displayed.
:Author Email: Email of the plugin author to be displayed.


To check all options, call the help command:

.. code-block:: bash

   >>> alfasim-sdk new --help

After the execution of the :program:`new` command the generated plugin project will have the following structure:

.. code-block:: bash

    \---myplugin
        |   CMakeLists.txt
        |   tasks.py
        |
        +---assets
        |       plugin.yaml
        |       README.md
        |
        \---src
            |   CMakeLists.txt
            |   hook_specs.h
            |   myplugin.cpp
            |
            \---python
                    myplugin.py

The highlights here are for:

:plugin.yaml: File with all information about the plugin that will be used by |alfasim|.
:myplugin.py: Implementation of the hooks for customization of the user interface or the solver configuration hooks.
:myplugin.c:  Implementation of the hooks for customization of solver.

Refer to the :ref:`Plugin Structure section <plugin_structure-section>` for more details about how the folder and files are structured.
The section :ref:`plugin-by-example-section` shows how to create simple plugins that make use of the `User Interface Hooks` and the `Solver Hooks`.

An example of a plugin implementation is available `here <https://github.com/ESSS/alfasim-plugin-template>`_.

Invoke
------

Since version 0.17.0, |sdk| started using `pyinvoke`_ tasks in order facilitate and standardize the plugins development process
using pre-defined tasks. You should install ``invoke`` package in your previously created environment. A standard ``tasks.py`` file
is generated automatically by the :program:`new` command, which can be customized by the user if needed.

To list the tasks available, use:

.. code-block:: bash

    >>> cd myplugin
    >>> invoke --list

.. _pyinvoke: https://www.pyinvoke.org

Creating a package
------------------

From the plugin root directory, execute the command `invoke package`.
This command will compile your C/C++ implementation and include the shared libraries inside an `artifacts` directory and
the generated plugin on the root directory with the extension `hmplugin`.

.. code-block:: bash

    >>> cd myplugin
    >>> invoke package --package-name=myplugin

The plugin directory will have the following structure when executing from a `Windows Operating System`:

.. code-block:: bash

    \---myplugin
        |   CMakeLists.txt
        |   compile.py
        |   myplugin-1.0.0-win64.hmplugin
        |
        +---artifacts
        |       myplugin.dll
        |       myplugin.lib
        |
        +---assets
        |       plugin.yaml
        |       README.md
        |
        +---build
        |       < ... >
        |       < ... >
        |
        +---package
        |       myplugin.dll
        |       plugin.yaml
        |       README.md
        |
        \---src
            |   CMakeLists.txt
            |   hook_specs.h
            |   myplugin.cpp
            |
            \---python
                    myplugin.py

Installing the plugin
---------------------

With :file:`myplugin.hmplugin` file, it is now possible to install it on |alfasim| application.
At the menu bar select the `Plugin Manager` option, as illustrated in the figure below:

.. image:: /_static/images/quick_start/menu_bar.png

In the `Plugin Manager` window, install :file:`myplugin.hmplugin` file plugin.

.. image:: /_static/images/quick_start/plugin_manager_empty.png

By clicking on the plugin name, it is possible to visualize the content of the :file:`README.md` file.

.. image:: /_static/images/quick_start/plugin_manager_with_plugin.png

Restart the application and check the recently installed plugin available at the :guilabel:`Tree`.

.. image:: /_static/images/quick_start/tree_with_plugin.png
