Text Based Input
================

The |sdk| allows the user to create or edit a project for |alfasim| application by writing the project specification
directly in an text file.

There are two possible ways to write a project:

ALFAcase file (``.alfacase``):
    A file with a textual description of a complete case in text format (YAML).
    This file allows the user to write case files directly and execute them directly using the command line.
    Being a text file in a standard and well supported format, it also allows the user to execute complex workflows by
    manipulating the files using external software or programming languages, providing flexibility and power.

    .. note::

        :program:`ALFAcase` is also referenced as ``ALFAsim case file``


CaseDescription instance:
    A class that helps to generate a valid ``.alfacase`` file programmatically using |SDK| by instantiating a
    :class:`CaseDescription <alfasim_sdk.CaseDescription>` object to define an ``ALFAsim`` project.


To get quick and running with |sdk| you can read the :ref:`alfacase-quick-start-section` and the
:ref:`alfacase-syntax` sections

.. toctree::
    :maxdepth: 2
    :glob:

    alfacase
    case_description


After reading the quick start section and the :program:`ALFAcase` by example section,
check out these additional resources to help better understand all the elements and options available to configure a project:

.. toctree::
    :maxdepth: 2
    :glob:

    api_reference
