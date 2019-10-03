C/C++ API
=========

This page contains the full reference to C/C++ ``ALFAsim-SDK`` API .

.. contents::
    :depth: 3
    :local:

Enums
-----

.. doxygenenum:: error_code

.. doxygenenum:: GridScope

.. doxygenenum:: MultiFieldDescriptionScope

.. doxygenenum:: TimestepScope

.. doxygenenum:: StateVariable

Structs
-------

.. doxygenstruct:: VariableScope
    :members:

Functions
---------

Plugin Input Data (From user interface)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doxygenfunction:: get_plugin_input_data_boolean

.. doxygenfunction:: get_plugin_input_data_enum

.. doxygenfunction:: get_plugin_input_data_quantity

.. doxygenfunction:: get_plugin_input_data_string

.. doxygenfunction:: get_plugin_input_data_string_size

.. doxygenfunction:: get_plugin_input_data_file_content

.. doxygenfunction:: get_plugin_input_data_file_content_size

.. doxygenfunction:: get_plugin_input_data_table_quantity

.. doxygenfunction:: get_plugin_input_data_reference

Plugin Internal Data
~~~~~~~~~~~~~~~~~~~~

.. doxygenfunction:: set_plugin_data

.. doxygenfunction:: get_plugin_data

.. doxygenfunction:: get_number_of_threads

.. doxygenfunction:: get_thread_id

ALFAsim's Solver Data
~~~~~~~~~~~~~~~~~~~~~

.. doxygenfunction:: get_plugin_variable

.. doxygenfunction:: get_field_id

.. doxygenfunction:: get_primary_field_id_of_phase

.. doxygenfunction:: get_phase_id

.. doxygenfunction:: get_layer_id

.. doxygenfunction:: get_state_variable_array

.. warning::
    Changing the contents retrieved by this function (`out` array) has **UNDEFINED BEHAVIOR**.
    The user must **NEVER** change the contents returned by this function.

.. doxygenfunction:: get_simulation_array

.. warning::
    Changing the contents retrieved by this function (`out` array) has **UNDEFINED BEHAVIOR**.
    The user must **NEVER** change the contents returned by this function.
