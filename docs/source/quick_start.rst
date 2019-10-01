.. _quick-start-section:

Quick Start
===========


In this section, it's showed how to create a plugin from scratch within the template command available on ALFAsim-SDK.
After the construction of this template, you can easily customize your application to extended alfasim functionality.

This allows you to experience the complete workflow in a short time.


Set up the environment
----------------------

The ALFAsim-SDK is a python package that helps the developers in the process to create an application, to use
this tool it's necessary to have a Python Interpreter with at least version 3.6. For more details on `how to install Python check
the docs <https://www.python.org/downloads/>`_

.. note::

    It is recommended that you install the ALFAsim-SDK using a Python Virtual Environment.
    For more details, see Virtual Environments and Packages in Python documentation.

From a terminal, install the ALFASIM SDK from pip

.. code-block:: console

    pip install alfasim-sdk


Creating a Plugin
-----------------

Execute the ALFAsim-SDK template command, to generate an empty plugin

.. code-block:: console

    alfasim-sdk template

After the execution of the command above, a series of information will request such as:

  * **Plugin Caption**: Caption to be used across the user interface to identify the plugin.
  * **Plugin Id**: The name of the plugin to be referenced during the development.
  * **Author Name**: Name of the plugin author to be displayed.
  * **Author Email**: Email of the plugin author to be displayed.

.. code-block:: console

    >>> alfasim-sdk template
    -- Plugin Caption: Myplugin
    -- Plugin Id: myplugin
    -- Author Name: ESSS
    -- Author Email: alfasim@esss.co

A Plugin is a compressed bundle of files, that contains the following structure:

.. code-block:: console

    \---myplugin
        |   CMakeLists.txt
        |   compile.py
        |
        +---assets
        |       plugin.yaml
        |       README.md
        |
        \---src
                CMakeLists.txt
                hook_specs.h
                myplugin.c
                myplugin.py

The highlights here are for

.. option:: plugin.yaml

    File with all information about the plugin that will be used by ALFAsim.

.. option:: plugin.py

    Implementation of the hooks for customization of the UI interface, or the pre-solver hooks

.. option:: plugin.c

    Implementation of the hooks for customization of solver


Check out the :ref:`Plugin Structure section <plugin_structure-section>` for more details about how the folder and files are structured, and
also, check the :ref:`plugin-by-example-section` that shows how to create simple plugins that interact with the :option:`User Interface` and the :option:`Solver`.

Creating a package
------------------

To create a plugin for ALFAsim, it's possible to execute the command `alfasim-sdk package` on the root directory
of your plugin.

This command will compile your C/C++ implementation and inserting the generated artifacts into your plugin.

.. code-block:: console

    >>> cd myplugin
    >>> alfasim-sdk package
    -- Package Name: myplugin

After the compilation part, a file name `myplugin.hmplugin` will be created in the same directory as the commands were invoked.

Installing the package on ALFAsim
---------------------------------

With the `myplugin.hmplugin` in hands, you can install it on ALFAsim application through the :option:`Plugin Manager`
:menuselection:`From the menu bar select: Plugins --> Plugin Manager --> Install plugin`
