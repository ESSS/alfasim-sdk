.. _case-description-quick-start-section:

Quick Start
===========

In this section, it is shown how to work with a ``CaseDescription`` and how to convert an :program:`ALFAcase`
from an existent project (exported from ALFAsim) to a ``Description``.

CaseDescription
---------------

The ``CaseDescription`` is a Python class that helps users to create a valid ``.alfacase`` file programmatically, by instantiating a
:class:`CaseDescription <alfasim_sdk.CaseDescription>` object.

To create a ``CaseDescription`` instance it is necessary to have a Python Interpreter with at least version 3.6 and the
|sdk| Python package.


.. note::

    For more details on how to install Python `check the official docs <https://www.python.org/downloads/>`_.
    It is recommended that you install the |sdk| using a Python Virtual Environment.
    For more details, see `Virtual Environments and Packages in Python documentation <https://docs.python.org/3/tutorial/venv.html>`_.


From a terminal, and inside a virtual environment, update pip:

>>> python -m pip install -U pip

Install the |sdk| with:

>>> pip install alfasim-sdk

.. note::

    All classes and constants that will be used to configure a project can be accessed through the main module of ``alfasim_sdk``


See section :ref:`alfacase-reference-section` for all available classes and options,
as well as which types and validators are applied at the time of object instantiation.

Knowing the type is important to create instantiate a class properly. For example, if you try to create a
:class:`NodeDescription <alfasim_sdk.NodeDescription>`, the ``node_type`` attribute
must be a string of one of the options available on :class:`NodeCellType <alfasim_sdk.NodeCellType>`, otherwise, a
``ValueError`` is raised.

.. code-block:: python

    >>> import alfasim_sdk
    >>> alfasim_sdk.NodeDescription(name="Node", node_type=1)
    [ ... ]
    ValueError: 'node_type' must be in <enum 'NodeCellType'> (got 1)

    >>> alfasim_sdk.NodeDescription(name='Node', node_type=alfasim_sdk.NodeCellType.Pressure)


As already informed at the beginning of the section, ALFAsim accepts only ``.alfacase`` files, the description classes
are only tools that help the creation and manipulation of a project programmatically in an easier way.

To convert a ``Description`` to alfacase you can use the function ``convert_description_to_alfacase`` and to convert a
``.alfacase`` file to ``Description`` you can use the function ``convert_alfacase_to_description``.


Convert an ALFAsim Project to a Description
-------------------------------------------

One of the easiest ways to create a ``.alfacase`` file is converting an existent project from an ALFAsim application.
It's also possible to convert this ``.alfacase`` file to a ``Description`` class using the function ``convert_alfacase_to_description``.

First, open an existing project and export it using the option :code:`Export ALFAsim Case file...` as illustrated in the figure below:

.. image:: /_static/images/alfacase/export_alfacase.png

The generated file will contain all project settings, including the default values used by ALFAsim.

In a Python file, import the ``alfasim_sdk`` module and call the ``convert_alfacase_to_description`` function informing the
file path of the ``.alfacase`` file.

.. code-block:: python

    >>> from pathlib import Path
    >>> alfacase_file_path = Path("...")

    >>> from alfasim_sdk import convert_alfacase_to_description
    >>> case_description_from_alfacase = convert_alfacase_to_description(alfacase_file_path)

Check out the :ref:`case-description-example` section that shows how to create a simple project from scratch and gives a walkthrough
of the main points necessary to configure a project.
