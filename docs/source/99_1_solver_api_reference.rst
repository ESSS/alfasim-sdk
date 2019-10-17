.. _sdk_api:

C/C++ API
=========

Here is listed the completed API available to implement the :ref:`solver_hooks`.

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

.. doxygenenum:: WallLayerProperty

.. doxygenenum:: sdk_load_error_code

Structs
-------

.. doxygenstruct:: VariableScope
    :members:


Functions
---------

.. _sdk_api_loading:

ALFAsim-SDK API Loading
~~~~~~~~~~~~~~~~~~~~~~~
.. Note::
    The ALFAsim-SDK API must be loaded with :cpp:func:`alfasim_sdk_open` inside :py:func:`HOOK_INITIALIZE<alfasim_sdk.hook_specs.initialize>`
    of any plugin, otherwise the plugin will not be able to use any function available in the API. In addition, to avoid memory
    leak it is important to unload the ALFAsim-SDK API in the last called `hook`, :py:func:`HOOK_FINALIZE<alfasim_sdk.hook_specs.finalize>`,
    using the :cpp:func:`alfasim_sdk_close` function.

.. doxygenfunction:: alfasim_sdk_open

.. doxygenfunction:: alfasim_sdk_close

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

.. doxygenfunction:: get_plugin_input_data_multiplereference_selected_size

.. _plugin_internal_data:

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

.. doxygenfunction:: get_simulation_tracer_array

.. warning::
    Changing the contents retrieved by this function (`out` array) has **UNDEFINED BEHAVIOR**.
    The user must **NEVER** change the contents returned by this function.

.. doxygenfunction:: get_simulation_quantity

.. doxygenfunction:: get_tracer_id

.. doxygenfunction:: get_tracer_name_size

.. doxygenfunction:: get_tracer_name

.. doxygenfunction:: get_tracer_ref_by_name

.. doxygenfunction:: get_tracer_partition_coefficient

.. doxygenfunction:: get_wall_interfaces_temperature

.. doxygenfunction:: get_wall_layer_id

.. doxygenfunction:: set_wall_layer_property

.. doxygenfunction:: get_flow_pattern
