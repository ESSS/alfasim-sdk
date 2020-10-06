.. _sdk_api:

C/C++ API
=========

Here is listed the completed API available to implement the :ref:`solver_hooks`.

.. contents::
    :depth: 2
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
    The |sdk| API must be loaded with :cpp:func:`alfasim_sdk_open` inside :py:func:`HOOK_INITIALIZE<alfasim_sdk.hook_specs.initialize>`
    of any plugin, otherwise the plugin will not be able to use any function available in the API. In addition, to avoid memory
    leak it is important to unload the |sdk| API in the last called `hook`, :py:func:`HOOK_FINALIZE<alfasim_sdk.hook_specs.finalize>`,
    using the :cpp:func:`alfasim_sdk_close` function.

.. doxygenfunction:: alfasim_sdk_open

.. doxygenfunction:: alfasim_sdk_close

.. _plugin_input_data:

Plugin Input Data (From user interface)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
    All API functions on this section has the parameter ``var_name``. This parameter must be filled following the rules
    exposed in :ref:`var_name_parsing` section.

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
    The plugin must **NEVER** change the contents returned by this function.

.. doxygenfunction:: get_simulation_array

.. warning::
    Changing the contents retrieved by this function (`out` array) has **UNDEFINED BEHAVIOR**.
    The plugin must **NEVER** change the contents returned by this function.

.. doxygenfunction:: get_simulation_tracer_array

.. warning::
    Changing the contents retrieved by this function (`out` array) has **UNDEFINED BEHAVIOR**.
    The plugin must **NEVER** change the contents returned by this function.

.. doxygenfunction:: get_simulation_quantity

.. doxygenfunction:: get_tracer_id

.. doxygenfunction:: get_tracer_name_size

.. doxygenfunction:: get_tracer_name

.. doxygenfunction:: get_tracer_ref_by_name

.. doxygenfunction:: get_tracer_partition_coefficient

.. doxygenfunction:: get_wall_interfaces_temperature

.. doxygenfunction:: get_flow_pattern


Unit Cell Model (UCM) helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doxygenfunction:: get_ucm_friction_factor_input_variable

.. doxygenfunction:: get_ucm_fluid_geometrical_properties


.. _var_name_parsing:

Variable Name Parsing
~~~~~~~~~~~~~~~~~~~~~

To retrieve input data from the plugin's GUI, the plugin must pass a ``var_name`` in a specific format. API functions that use this
kind of variable described on :ref:`plugin_input_data` section.

All variables must begin with the model name described on the plugin model, followed by ``.`` (For nested objects) or
``->`` (For references). Lists must be accessed with the list index directly, for example, ``Model.lst[0]`` will be the
first element of the list "lst", inside the plugin model named "Model". References can be internal (Reference to a plugin model)
or external (Reference to an ALFAsim model).

Basic example
*************

Imagine you have the following simple GUI model defined as

.. code-block:: python

    @data_model(icon='', caption='Plugin Model')
    class Model:
        boolean_data = Boolean(value=True, caption="BOOLEAN CAPTION")

To extract the plugin input data content on C++, the plugin must use the proper API function call:

.. code-block:: c++

    int errcode = 0;
    bool test_api_boolean = false;
    errcode = alfasim_sdk_api.get_plugin_input_data_boolean(
        ctx, &test_api_boolean, get_plugin_id(), "Model.boolean_data");
    std::cout << " BOOLEAN:" << test_api_boolean
              << " ERROR CODE:" << errcode
              << std::endl;

See :cpp:func:`get_plugin_input_data_boolean` for details.

List Model Example
******************

For the cases were the model is a container, it is possible to retrieve the information for each element individually.

.. code-block:: python

    @data_model(icon='', caption='Plugin Model 2')
    class Model:
        name = String(value='default', caption='Name')
        boolean = Boolean(value=True, caption="Boolean")
        quantity = Quantity(value=1, unit='m', caption='Quantity')


    @container_model(icon='', caption='Plugin Container', model=Model)
    class ModelContainer:
        pass

To extract the plugin input data content on C++, the plugin must use the proper API function call:

.. code-block:: c++

    int errcode = 0;
    double test_api_quantity = 0.;
    errcode = alfasim_sdk_api.get_plugin_input_data_quantity(
       ctx, &test_api_quantity, get_plugin_id(), "ModelContainer[0].quantity");
    std::cout << " Quantity from container[0]:" << test_api_quantity
              << " ERROR CODE:" << errcode
              << std::endl;

See :cpp:func:`get_plugin_input_data_quantity` for details.

Internal Reference Example
**************************

Internal references are references to models defined in the plugin itself. They are useful when you have a list of models,
for example, but need to let the user decide from one specific model from the list. Assuming the model container defined
in the previous, example, an internal reference for an element inside that container can be programmed as follows. The plugin
must use ``->`` to access referenced data, instead of ``.`` as in other examples.

.. code-block:: python

    @data_model(icon='', caption='Plugin Model')
    class OtherModel:
        internal_reference = Reference(
            container_type='ModelContainer',
            ref_type=Model,
            caption="Internal Reference"
        )

Data from the referenced model can then be extracted on C++ code as follows. Note that the developer will extract the
values directly, not the model itself, that is, in the example below, there is never an object of type ``Model``.
Raw data values such as boolean, strings or floats are directly retrieved instead.

.. code-block:: c++

    int errcode = 0;
    double test_api_quantity = 0.;
    errcode = alfasim_sdk_api.get_plugin_input_data_quantity(
        ctx, &test_api_quantity, get_plugin_id(), "OtherModel.internal_reference->quantity");
    std::cout << " Quantity from internal reference:" << test_api_quantity
              << " ERROR CODE:" << errcode
              << std::endl;

External Reference Example
**************************

External references gives the user a way to interact with references to specific |alfasim|'s GUI object configurations.
Those types of references work a bit different, because |alfasim| developers must provide an API for each specific entity.
As of today, the only exposed |alfasim| model is the Tracer model. See the tracer-related functions to have an overview
about the available data that can be used:

 - :cpp:func:`get_simulation_tracer_array`
 - :cpp:func:`get_tracer_id`
 - :cpp:func:`get_tracer_name`
 - :cpp:func:`get_tracer_ref_by_name`
 - :cpp:func:`get_tracer_partition_coefficient`

The example below extracts the `tracer Id` configured in the plugin.

.. code-block:: python

    @data_model(icon='', caption='Plugin Model')
    class OtherModel:
        tracer_reference = Reference(
            ref_type=TracerType,
            caption="Tracer Reference",
        )

To extract the plugin input data content on C++, the plugin must use the proper API function call:

.. code-block:: c++

    int errcode = 0;
    void* tracer_ref = nullptr;
    errcode = get_plugin_input_data_reference(
        ctx, &tracer_ref, get_plugin_id(), "OtherModel.tracer_reference");

    int tracer_id = -1;
    errcode = get_tracer_id(ctx, &tracer_id, tracer_ref);
    std::cout << "TRACER ID: " << tracer_id << std::endl;

See :cpp:func:`get_plugin_input_data_reference` for details.

Multiple Reference
******************

The plugin developer may need to let the user select not one, but several references (This is valid for both internal
and external references). To tackle this problem, |alfasim| developers created the notion of Multiple References.
It is basically a container of referenced objects, and the usage is simply a mix of the container with the reference
syntax.

Example of a GUI model in which has both types of multiple references:

.. code-block:: python

    @data_model(icon='', caption='Plugin Model')
    class OtherModel:
        multiple_reference = MultipleReference(
            ref_type=TracerType,
            caption='Multiple Reference'
        )

        internal_multiple_reference = MultipleReference(
            ref_type=Model,
            container_type='ModelContainer',
            caption='Internal Multiple Reference'
        )

Example of accessing the external multiple references:

.. code-block:: c++

    int errcode = -1;
    int indexes_size = -1;
    errcode = get_plugin_input_data_multiplereference_selected_size(
        ctx, &indexes_size, get_plugin_id(), "OtherModel.multiple_reference");

    void* tracer_ref = nullptr;
    for (int i = 0; i < indexes_size; ++i) {
        auto reference_str = std::string(
            "OtherModel.multiple_reference[" + std::to_string(i) + "]");
        errcode = get_plugin_input_data_reference(
            ctx, &tracer_ref, get_plugin_id(), reference_str.c_str());

        int tracer_id = -1;
        errcode = get_tracer_id(ctx, &tracer_id, tracer_ref);
        std::cout << "TRACER ID: " << tracer_id << std::endl;
    }

Example of accessing the internal multiple references:

.. code-block:: c++

   int errcode = -1;
    int indexes_size = -1;
    errcode = get_plugin_input_data_multiplereference_selected_size(
        ctx,
        &indexes_size,
        get_plugin_id(),
        "OtherModel.internal_multiple_reference");

    for (int i = 0; i < indexes_size; ++i) {
        auto test_api_bool = false;
        auto reference_str = std::string(
            "OtherModel.internal_multiple_reference[" + std::to_string(i) + "]->boolean");
        errcode = get_plugin_input_data_boolean(
            ctx,
            &test_api_bool,
            get_plugin_id(),
            reference_str.c_str());
        std::cout << " Bool from referenced container[" << i << "]:" << (test_api_bool ? "true" : "false")
                  << " ERROR CODE:" << errcode
                  << std::endl;
    }

see :cpp:func:`get_plugin_input_data_multiplereference_selected_size` for details.
