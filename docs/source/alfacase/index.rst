ALFAcase
========

The |sdk| allows the user to create or edit a project for |alfasim| application by writing the project specification
directly in an :program:`ALFAcase` file, which is a text document that contains all the definitions to assemble a project.

The purpose of the :program:`ALFAcase` files is to allow the management of the project directly from a file rather
than opening the application. It's also possible to assemble a project using
Python by creating an instance of a CaseDescription filling with all relevant information and using the |sdk| to
export this class to a :program:`ALFAcase` file.

To get quick and running with |sdk| you can read the :ref:`alfacase-quick-start-section` and the
:ref:`alfacase-syntax` sections

.. toctree::
    :maxdepth: 2
    :glob:

    01_alfacase_quick_start
    02_alfacase_syntax
    03_alfacase_example


After reading the quick start section and the :program:`ALFAcase` by example section,
check out these additional resources to help better understand all the elements and options available to configure a project:

.. toctree::
    :maxdepth: 2
    :glob:

    04_case_description_quick_start
    05_case_description_by_example
    api_reference
