from hookman.hooks import HookSpecs


def initialize(ctx: "void*") -> "int":
    """
    **c++ signature** : ``HOOK_INITIALIZE(void* ctx)``

    This `hook` allows the plugin to initialize its internal data and also some
    simulator configurations available via API. If any API function is used
    the `ALFAsim-SDK` API must be loaded, see :ref:`sdk_api_loading` section
    for more information.

    :param ctx: ALFAsim's plugins context
    :returns: Return OK if successful or anything different if failed

    Examples of usage:

    A minimal ``HOOK_INITIALIZE`` needed could be:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 3

        ALFAsimSDK_API alfasim_sdk_api;

        HOOK_INITIALIZE(ctx) {
            const char* plugin_id = get_plugin_id()
            // Loading ALFAsim-SDK API
            int load_error_code = alfasim_sdk_open(alfasim_sdk_api)
            if (load_error_code != 0){
                return load_error_code;
            }
            return OK;
        }

    Where ``OK`` is an :cpp:enum:`error_code` value and ``get_plugin_id()`` function is created automatically
    to each plugin template and accessible from ``hook_specs.h`` file. As can be seen in the example above at
    least the ``ALFAsim-SDK`` API should be loaded.

    However, if the plugin has internal data the minimal ``HOOK_INITIALIZE`` implementation would be

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 3

        ALFAsimSDK_API alfasim_sdk_api;

        HOOK_INITIALIZE(ctx)
        {
            const char* plugin_id = get_plugin_id()
            // Loading ALFAsim-SDK API
            int load_error_code = alfasim_sdk_open(alfasim_sdk_api)
            if (load_error_code != 0){
                return load_error_code;
            }
            // Threads Information
            int n_threads = -1;
            int errcode = alfasim_sdk_api.get_number_of_threads(
                ctx, &n_threads);
            if (errcode != 0){
                return errcode;
            }
            // Setting internal data to each thread
            for (int thread_id = 0; thread_id < n_threads; ++thread_id){
                double value;
                alfasim_sdk_api.get_plugin_input_data_quantity(
                    ctx, &value, plugin_id, thread_id);
                void* data = new double(value);
                alfasim_sdk_api.set_plugin_data(
                    ctx, plugin_id, data, thread_id);
            }
            return OK;
        }

    It is important to note that ``void* data`` at line 22 could be a more complex data structure, like a
    class object for example.
    """


def finalize(ctx: "void*") -> "int":
    """
    **c++ signature** : ``HOOK_FINALIZE(void* ctx)``

    This Hook must be used to delete all plugin internal data and unload the `ALFAsim-SDK` API.
    Otherwise, a memory leak could occur from your plugin.

    :param ctx: ALFAsim's plugins context
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_FINALIZE(ctx)
        {
            // Threads information
            int n_threads = -1;
            int errcode = alfasim_sdk_api.get_number_of_threads(ctx, &n_threads);
            if (errcode != 0){ // or errcode != OK
                return errcode;
            }
            const char* plugin_id = get_plugin_id();
            // Plugin internal data
            for (int thread_id = 0; thread_id < n_threads; ++thread_id) {
                void* data = nullptr;
                errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, &data, plugin_id, thread_id);
                delete data;
            }
            // Unloading ALFAsim-SDK API
            int load_error_code = alfasim_sdk_close(alfasim_sdk_api)
            if (load_error_code != 0){
                return load_error_code;
            }
            return OK;
        }

    Where ``OK`` is an :cpp:enum:`error_code` value.
    """


def update_plugins_secondary_variables(ctx: "void*") -> "int":
    """
    **c++ signature** : ``HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES(void* ctx)``

    Internal simulator hook to update plugin's secondary variables.
    This is called as the last step on ALFAsim's update internal secondary variables workflow.

    :param ctx: ALFAsim's plugins context
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES(ctx)
        {
            int errcode = -1;
            int size_U = -1;
            int size_E = -1;
            int liq_id = -1;
            errcode = alfasim_sdk_api.get_field_id(
                ctx, &oil_id, "oil");
            double* vel;
            VariableScope Fields_OnFaces = {
                GridScope::FACE,
                MultiFieldDescriptionScope::FIELD,
                TimestepScope::CURRENT
            }
            errcode = alfasim_sdk_api.get_simulation_array(
                ctx, &vel, (char*) "U", Fields_OnFaces, liq_id, &size_U);
            double* kinetic_energy;
            char* name = "kinetic_energy_of_oil";
            int global_idx = 0;
            errcode = alfasim_sdk_api.get_plugin_variable(
                ctx,
                (void**) (&kinetic_energy),
                name,
                global_idx,
                TimestepScope::CURRENT,
                &size_E);
            if (size_U != size_E){
                return OUT_OF_BOUNDS;
            }
            for (int i =0; i < size_U; ++i){
                kinetic_energy[i] = vel[i] * vel[i] / 2.;
            }
            return OK;
        }

    In the example above the variable ``kinetic_energy_of_oil`` was registered as a global variable, but its value is
    obtained for `oil field`. If this variable would be calculated to all fields then the ``global_idx`` would be
    substituted by ``field_idx`` and it would be performed to each `field`.
    """


def update_plugins_secondary_variables_on_first_timestep(ctx: "void*") -> "int":
    """
    **c++ signature** : ``HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES_ON_FIRST_TIMESTEP(void* ctx)``

    Internal simulator hook to update plugin's secondary variables on the first timestep.
    This is called as the first step on ALFAsim's update internal variables workflow.
    This method is specially important when you have a plugin which the secondary variables depend
    on `old` values. In the first timestep, there is no `old` values, so you may use this hook
    to initialize your variables contents.

    :param ctx: ALFAsim's plugins context
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES_ON_FIRST_TIMESTEP(ctx)
        {
            int errcode = -1;
            int size_E = -1;
            double* kinetic_energy;
            char* name = "kinetic_energy_of_oil";
            int global_idx = 0;
            errcode = alfasim_sdk_api.get_plugin_variable(
                ctx,
                (void**) (&kinetic_energy),
                name,
                global_idx,
                TimestepScope::CURRENT,
                &size_E);
            for (int i =0; i < size_U; ++i){
                kinetic_energy[i] = 0.0;
            }
            return OK;
        }

    """


def update_plugins_secondary_variables_on_tracer_solver(ctx: "void*") -> "int":
    """
    **c++ signature** : ``HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES_ON_TRACER_SOLVER(void* ctx)``

    Internal simulator hook to update plugin's secondary variables in the Tracer Solver scope.
    Tracer Solver is used to solve the tracer transport equation.
    This is called as the last step on ALFAsim's Tracer Solver update variables workflow.

    :param ctx: ALFAsim's plugins context
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_UPDATE_PLUGINS_SECONDARY_VARIABLES_ON_TRACER_SOLVER(ctx)
        {
            const char* plugin_id = get_plugin_id()
            int errcode = -1;
            int size_t = -1;
            int size_p_var = -1;
            int liq_id = -1;
            errcode = alfasim_sdk_api.get_field_id(
                ctx, &oil_id, "oil");
            double* tracer_mass_fraction;
            VariableScope global_OnCenters = {
                GridScope::FACE,
                MultiFieldDescriptionScope::FIELD,
                TimestepScope::CURRENT
            }
            // Tracer information
            void* tracer_ref;
            errcode = alfasim_sdk_api.get_tracer_ref_by_name(
                ctx,
                &tracer_ref,
                "my_tracer", // Added by User interface
                plugin_id);
            int tracer_id = -1;
            errcode = alfasim_sdk_api.get_tracer_id(
                ctx, &tracer_id, tracer_ref);
            double *tracer_mass_fraction
            errcode = alfasim_sdk_api.get_simulation_tracer_array(
                ctx,
                &tracer_mass_fraction,
                (char*) "phi",
                global_OnCenters,
                tracer_id,
                0,  // GLOBAL
                &size_t);
            // Plugin secondary variable array
            double* plugin_var;
            errcode = alfasim_sdk_api.get_plugin_variable(
                ctx,
                (void**) (&plugin_var),
                name,
                0,  // GLOBAL
                TimestepScope::CURRENT,
                &size_p_var);
            if (size_t != size_p_var){
                return OUT_OF_BOUNDS;
            }
            for (int i =0; i < size_t; ++i){
                // Do some calculations with plugin_var
                // using tracer_mass_fraction values
            }
            return OK;
        }

    Note that functions like :cpp:func:`get_tracer_ref_by_name`, :cpp:func:`get_tracer_id` and
    :cpp:func:`get_simulation_tracer_array` were used to obtain information related to tracers.
    """


def calculate_mass_source_term(
    ctx: "void*", mass_source: "void*", n_fields: "int", n_control_volumes: "int"
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_MASS_SOURCE_TERM(void* ctx, void* mass_source, int n_fields, int n_control_volumes)``

    Internal simulator hook to calculate source terms of mass equation. This is called after all residual functions are
    evaluated.

    The plugin is supposed to change the given ``mass_source`` array pointer. Its values are contiguous in memory
    and the dimensions are given by ``n_fields`` and ``n_control_volumes``. It has unit equal to ``[kg/s]``.

    :param ctx: ALFAsim's plugins context
    :param mass_source: Source term of mass equation
    :param n_fields: Number of fields
    :param n_control_volumes: Number of control volumes
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_MASS_SOURCE_TERM(
            ctx, mass_source, n_fields, n_control_volumes)
        {
            int oil_id = -1;
            errcode = alfasim_sdk_api.get_field_id(
                ctx, &oil_id, "oil");
            // Convertion from void* to double* and getting the
            // array range related to oil field
            double* oil_mass_source =
                (double*) mass_source + n_control_volumes * oil_id;
            // Make some calculations and add it to oil_mass_source.
            // In this example, we add a mass source of 3.1415 kg/s to all control volumes.
            for (int i = 0; i < n_control_volumes; ++i) {
                oil_mass_source[i] = 3.1415; // [kg/s]
            }
            return OK;
        }

    In the example above is shown how to manage the ``mass_source`` array to get the mass source term array related to a
    specific field (`oil field` in this case). Note that ``oil_mass_source`` has size equal to ``n_control_volumes``.

    """


def calculate_momentum_source_term(
    ctx: "void*", momentum_source: "void*", n_layers: "int", n_faces: "int"
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_MOMENTUM_SOURCE_TERM(void* ctx, void* momentum_source, int n_layers, int n_faces)``

    Internal simulator hook to calculate source terms of momentum equation. This is called after all residual functions
    are evaluated.

    The plugin is supposed to change the given ``momentum_source`` array pointer. Its values is contiguous in memory
    and the dimensions are given by ``n_layers`` and ``n_faces``. It has unit equal to ``[N]``.

    :param ctx: ALFAsim's plugins context
    :param momentum_source: Source term of momentum equation
    :param n_layers: Number of layers
    :param n_faces: Number of faces (equal to n_control_volumes minus 1)
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_MOMENTUM_SOURCE_TERM(
            ctx, momentum_source, n_layers, n_faces)
        {
            int gas_id = -1;
            errcode = alfasim_sdk_api.get_layer_id(
                ctx, &gas_id, "gas");
            // Convertion from void* to double* and getting the
            // array range related to gas layer
            double* gas_momentum_source =
                (double*) momentum_source + n_faces * gas_id;
            // Make some calculations and add it to gas_momentum_source
            return OK;
        }

    In the example above is shown how to manage the ``momentum_source`` array to get the momentum source term array
    related to a specific layer (`gas layer` in this case). Note that ``gas_momentum_source`` has size equal to
    ``n_faces``.

    """


def calculate_energy_source_term(
    ctx: "void*",
    energy_source: "void*",
    n_energy_equation: "int",
    n_control_volumes: "int",
) -> "int":
    """
     **c++ signature** : ``HOOK_CALCULATE_ENERGY_SOURCE_TERM(void* ctx, void* energy_source, int n_energy_equation, int n_control_volumes)``

    Internal simulator hook to calculate source terms of energy equation. This is called after all residual functions
    are evaluated.

    The plugin is supposed to change the given ``energy_source`` array pointer. Its values is contiguous in memory
    and the dimensions are given by ``n_energy_equation`` and ``n_control_volumes``. It has unit equal to ``[J/s]``.

    Since ``ALFAsim`` considers two energy models, if ``n_energy_equation`` is equal to 1 it means that the global energy model
    is being used. Otherwise the layers energy model is being used. See the ``ALFAsim``'s Technical Report for more
    information about the equations system.

    :param ctx: ALFAsim's plugins context
    :param energy_source: Source term of energy equation
    :param n_energy_equation: Number of Energy Equation being solved
    :param n_control_volumes: Number of control volumes
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_ENERGY_SOURCE_TERM(
            ctx, energy_source, n_energy_equation, n_control_volumes)
        {
            double* gas_energy_source;
            if (n_energy_equation > 1){
                // Layers Energy model
                // One energy equation for each layer
                int gas_id = -1;
                errcode = alfasim_sdk_api.get_layer_id(
                    ctx, &gas_id, "gas");
                // Convertion from void* to double* and getting the
                // array range related to gas layer
                gas_energy_source =
                    (double*) energy_source + n_faces * gas_id;
            } else {
                // Global energy model
                // Only one global energy equation

                // Convertion from void* to double*
                gas_energy_source = (double*) energy_source;
            }
            // Make some calculations and add it to gas_energy_source
            return OK;
        }

    In the example above is shown how to manage the ``energy_source`` array to get the energy source term array
    related to a specific layer (`gas layer` in this case). Note that ``gas_energy_source`` has size equal to
    ``n_control_volumes``.

    """


def calculate_tracer_source_term(
    ctx: "void*", phi_source: "void*", n_tracers: "int", n_control_volumes: "int"
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_TRACER_SOURCE_TERM(void* ctx, void* phi_source, int n_tracers, int n_control_volumes)``

    Internal simulator hook to calculate source terms of tracer transport equation. This is called after all residual
    functions are evaluated.

    The plugin is supposed to change the given ``phi_source`` array pointer. Its values is contiguous in memory
    and the dimensions are given by ``n_tracers`` and ``n_control_volumes``. It has unit equal to ``[kg/s]``.

    :param ctx: ALFAsim's plugins context
    :param phi_source: Source term of tracers mass equation
    :param n_tracers: Number of tracers
    :param n_control_volumes: Number of control volumes
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_TRACER_SOURCE_TERM(
            ctx, phi_source, n_tracers, n_control_volumes)
        {
           // Tracer information
            void* tracer_ref;
            errcode = alfasim_sdk_api.get_tracer_ref_by_name(
                ctx,
                &tracer_ref,
                "my_tracer", // Added by User interface
                plugin_id);
            int tracer_id = -1;
            errcode = alfasim_sdk_api.get_tracer_id(
                ctx, &tracer_id, tracer_ref);
            // Convertion from void* to double* and getting the
            // array range related to gas layer
            double* my_tracer_phi_source =
                (double*) phi_source + n_control_volumes * tracer_id;
            // Make some calculations and add
            // it to my_tracer_phi_source
            return OK;
        }

    In the example above is shown how to manage the ``phi_source`` array to get the tracer source term array
    related to a specific tracer (`my_tracer` in this case). Note that ``gas_energy_source`` has size equal to
    ``n_control_volumes``.

    """


def initialize_state_variables_calculator(
    ctx: "void*",
    P: "void*",
    T: "void*",
    T_mix: "void*",
    phi: "void*",
    n_control_volumes: "int",
    n_layers: "int",
    n_tracers: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_INITIALIZE_STATE_VARIABLES_CALCULATOR(void* ctx, void* P, void* T, void* T_mix,
    void* phi, int n_control_volumes, int n_layers, int n_tracers)``

    Hook for the state variables calculator initialization (internal ``ALFAsim`` structure).

    At this point, it is possible to pre-calculate and cache any relevant information. Then, for each state variable of
    the phases in the python configuration file, the `hook` :py:func:`HOOK_CALCULATE_STATE_VARIABLE<alfasim_sdk._internal.hook_specs.calculate_state_variable>`
    is called and return the pre-calculated values.

    :param ctx: ALFAsim's plugins context
    :param P: Pressure values array
    :param T: Temperature values array
    :param T_mix: Mixture temperature values array
    :param phi: Tracer mass fraction values array
    :param n_control_volumes: Number of control volumes
    :param n_layers: Number of layers
    :param n_tracers: Number of tracers in the system
    :returns: Return OK if successful or anything different if failed

    The ``P`` and ``T_mix`` have size equal to ``n_control_volumes``. However, ``T`` has values contiguous in memory
    and its dimensions are given by ``n_layers`` and ``n_control_volumes``. Finally, ``phi`` dimensions are given by
    ``n_tracers`` and ``n_control_volumes``.

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_INITIALIZE_STATE_VARIABLES_CALCULATOR(
            ctx, P, T, T_mix, phi, n_control_volumes, n_layers, n_tracers)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            // MyStruct is a developer defined struct to hold
            // all important information for plugin hooks.
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            // MyFunction is a function implemented by
            // plugin developer that computes de density
            data.density = MyFunction(P, T_mix, n_control_volumes);
            return OK;
        }
        // Then, to use the cached value:
        HOOK_CALCULATE_STATE_VARIABLE(
            ctx, P, T, n_control_volumes, phase_id, field_id, property_id, output)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            if (phase_id != data.my_added_phase_id) {
                return OK;
            }
            if (property_id == StateVariable::RHO) {
                for (int i = 0; i < n_control_volumes; ++i) {
                    output[i] = data.density[i];
                }
            }
            return OK;
        }

    .. Note::
        For pre-calculated values, the plugin developer must cache it in the plugin internal data. See the example above.

    However, if the state variable is considered constant or the developer doesn't need to cache the values,
    just return ``OK``.

    """


def calculate_state_variable(
    ctx: "void*",
    P: "void*",
    T: "void*",
    n_control_volumes: "int",
    phase_id: "int",
    field_id: "int",
    property_id: "int",
    output: "void*",
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_STATE_VARIABLE(void* ctx, void* P, void* T, int n_control_volumes,
    int phase_id, int field_id, int property_id, void* output)``

    Hook to calculate the state variable given by the `property_id` (See :cpp:enum:`StateVariable` values), for the
    phase with `phase_id` (Note that the phase id is the same as the one retrieved from the :cpp:func:`get_phase_id` API
    function - It is not advisable to use hardcoded numbers).

    List of affected variables:|br|
    - ``Density`` |br|
    - ``Viscosity`` |br|
    - ``Heat Capacity`` |br|
    - ``Partial Derivative of Density in Relation to Pressure`` |br|
    - ``Partial Derivative of Density in Relation to Temperature`` |br|
    - ``Enthalpy`` |br|
    - ``Thermal Conductivity`` |br|

    :param ctx: ALFAsim's plugins context
    :param P: Pressure values array
    :param T: Temperature values array
    :param n_control_volumes: Number of control volumes
    :param n_phase_id: Id of phase in which the property must be calculated
    :param n_field_id: Id of field in which the property must be calculated (Associated to the phase)
    :param property_id: A :cpp:enum:`StateVariable` value. It indicates which
                        property must be calculated
    :param output: Output values array
    :returns: Return OK if successful or anything different if failed

    The ``output`` parameter must be filled with the calculated property for each control volume. The
    pressure ``P`` and layer or mixture temperature ``T`` (Depending on the energy model being used)
    are given in order to perform the calculation. The number of control volumes is also given for
    convenience.

    In case of calculating all properties and caching them in the :py:func:`HOOK_INITIALIZE_STATE_VARIABLES_CALCULATOR<alfasim_sdk._internal.hook_specs.initialize_state_variables_calculator>`
    (depending on the model used inside the plugin) the ``field_id`` can be used to retrieve the cached
    properties for a specific field associated to the phase in which ``phase_id`` is informed. For
    example, when the energy model for layers is used in a simulation, fields of a phase may be in
    others layers ("oil in water" is located in the "water" layer) in which the temperature are different.


    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_STATE_VARIABLE(
            ctx, P, T, n_control_volumes, phase_id, field_id, property_id, output)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            if (phase_id != data.my_added_phase_id) {
                return OK;
            }
            if (property_id == StateVariable::RHO) {
                for (int i = 0; i < n_control_volumes; ++i) {
                    // If the property has a constant value
                    output[i] = data.constant_density;
                    // If the property must be computed
                    // MyStruct has a function called 'compute_density()'
                    output[i] = data.compute_density(
                        (double *)P[i], (double *)T[i]);
                }
            }
            return OK;
        }

    .. warning::
        The plugin developer must **NOT** change any variable other than the output. The ``output`` size is
        ``n_control_volumes`` .

    """


def calculate_phase_pair_state_variable(
    ctx: "void*",
    P: "void*",
    T_mix: "void*",
    n_control_volumes: "int",
    phase1_id: "int",
    phase2_id: "int",
    phase_pair_id: "int",
    property_id: "int",
    output: "void*",
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_PHASE_PAIR_STATE_VARIABLE(void* ctx, void* P, void* T_mix, int n_control_volumes,
    int phase1_id, int phase2_id, int phase_pair_id, int property_id, void* output)``

    Hook to calculate the state variable given by the `property_id` (See :cpp:enum:`StateVariable` values), for the phase
    pair `(phase1_id, phase2_id)` (Note that the phase id is the same as the one retrieved from the :cpp:func:`get_phase_id()`
    API function - It is not advisable to use hardcoded numbers).

    List of affected variables:|br|
    - ``Interfacial Tension``

    :param ctx: ALFAsim's plugins context
    :param P: Pressure values array
    :param T_mix: Mixture temperature values array
    :param n_control_volumes: Number of control volumes
    :param phase1_id: Id of phase one in which the property must be calculated
    :param phase2_id: Id of phase two in which the property must be calculated
    :param phase_pair_id: Id of the phase pair in which the property must be calculated
    :param property_id: A :cpp:enum:`StateVariable` value. It indicates which
                        property must be calculated
    :param output: Output values array
    :returns: Return OK if successful or anything different if failed

    The output parameter must be filled with the calculated property for each control volume. The
    pressure ``P`` and mixture temperature ``T_mix`` are given in order to perform the calculation.
    The number of control volumes is also given for convenience.

    Since the state properties calculated by this hook is performed for phase pairs, the information
    of the phases involved is provided by the ``phase_pair_id`` and also by the single phase IDs called
    ``phase1_id`` and  ``phase2_id``. To identify which ``phase_pair_id`` are being passed it is possible
    to retrieve the phase pair IDs by using :cpp:func:`get_phase_pair_id`.

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_PHASE_PAIR_STATE_VARIABLE(
            ctx, P, T_mix, n_control_volumes, phase1_id, phase2_id, phase_pair_id, property_id, output)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            int gas_phase_id = -1;
            errcode = alfasim_sdk_api.get_phase_id(
                ctx, &gas_phase_id, "gas");

            if ((
                (phase1_id == data.my_added_phase_id)
                && (phase1_id == gas_phase_id)
                ) || (
                (phase1_id == gas_phase_id)
                && (phase1_id == data.my_added_phase_id)
                ))
            {
                for (int i = 0; i < n_control_volumes; ++i) {
                    // If the property has a constant value
                    output[i] = data.constant_surface_tension;
                    // If the property must be computed
                    // MyStruct has a function
                    // called 'compute_surface_tension()'
                    output[i] = data.compute_surface_tension(
                        (double *)P[i], (double *)T_mix[i]);
                }
            }
            return OK;
        }

    .. warning::
        The plugin developer must **NOT** change any variable other than the output. The ``output`` size is
        ``n_control_volumes``.

    """


def finalize_state_variables_calculator(ctx: "void*") -> "int":
    """
    **c++ signature** : ``HOOK_FINALIZE_STATE_VARIABLES_CALCULATOR(void* ctx)``

    Hook for the state variables calculator finalization.
    The plugin developer should free/delete any allocated data from the :py:func:`HOOK_INITIALIZE_STATE_VARIABLE_CALCULATOR<alfasim_sdk._internal.hook_specs.initialize_state_variables_calculator>`.

    :param ctx: ALFAsim's plugins context
    :returns: Return OK if successful or anything different if failed

    If there is no need memory deallocation a minimal implementation would be:

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_FINALIZE_STATE_VARIABLES_CALCULATOR(ctx)
        {
            return OK;
        }

    """


def initialize_particle_diameter_of_solids_fields(
    ctx: "void*",
    particle_diameter: "void*",
    n_control_volumes: "int",
    solid_field_id: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_INITIALIZE_PARTICLE_DIAMETER_OF_SOLIDS_FIELDS(void* ctx, void* particle_diameter,
    int n_control_volumes, int solids_field_id)``

    Internal simulator hook to initialize particle diameter of solid fields. This `hook` follows the same idea of
    :py:func:`HOOK_UPDATE_PLUGIN_SECONDARY_VARIABLES_ON_FIRST_TIMESTEP<alfasim_sdk._internal.hook_specs.update_plugins_secondary_variables_on_first_timestep>`,
    which makes the initialization in the moment that there is no previous time step data available.

    :param ctx: ALFAsim's plugins context
    :param particle_diameter: Particle diameter of a given solid field,
    :param n_control_volumes: Number of control volumes,
    :param solid_field_id: Index of the solid field in which the `particle_diameter`
                           Should be calculated.
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_INITIALIZE_PARTICLE_DIAMETER_OF_SOLIDS_FIELDS(
            ctx, particle_diameter, n_control_volumes, solids_field_id)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            if (solids_field_id != data.my_added_solid_field_id) {
                return OK;
            } else {
                for (int i = 0; i < n_control_volumes; ++i) {
                    // If the particle size is constant
                    particle_diameter[i] = data.constant_particle_size;
                    // The value is calculated
                    // MyStruct has a function
                    // called 'initial_particle_size()'
                    particle_diameter[i] = data.initial_particle_size(
                             // List of params that can be
                             // retrieved by get_simulation_array()
                             );
                }
            }
            return OK;
        }

    """


def update_particle_diameter_of_solids_fields(
    ctx: "void*",
    particle_diameter: "void*",
    n_control_volumes: "int",
    solid_field_id: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_UPDATE_PARTICLE_DIAMETER_OF_SOLIDS_FIELDS(void* ctx, void* particle_diameter,
    int n_control_volumes, int solids_field_id)``

    Internal simulator hook to update/calculate particle diameter of solid fields. It is called right before any update
    secondary variable from |alfasim|'s Solver, because they may depend on the solids particle size (for example `Slurry
    Viscosity` calculated by ``Solids Model``)

    :param ctx: ALFAsim's plugins context
    :param particle_diameter: Particle diameter of a given solid field,
    :param n_control_volumes: Number of control volumes,
    :param solid_field_id: Index of the solid field in which the `particle_diameter`
                           Should be calculated.
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_UPDATE_PARTICLE_DIAMETER_OF_SOLIDS_FIELDS(
            ctx, particle_diameter, n_control_volumes, solids_field_id)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            if (solids_field_id != data.my_added_solid_field_id) {
                return OK;
            } else {
                for (int i = 0; i < n_control_volumes; ++i) {
                    // If the particle size is constant
                    particle_diameter[i] = data.constant_particle_size;
                    // The value is calculated
                    // MyStruct has a function
                    // called 'compute_particle_size()'
                    particle_diameter[i] = data.compute_particle_size(
                             // List of params that can be
                             // retrieved by get_simulation_array()
                             );
                }
            }
            return OK;
        }

    """


def calculate_slip_velocity(
    ctx: "void*",
    U_slip: "double*",
    solid_field_index: "int",
    layer_index: "int",
    n_faces: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_SLIP_VELOCITY(void* ctx, double* U_slip, int solid_field_index, int layer_index, int n_faces)``

    Internal `hook` to calculate slip velocity in the Solids Model.
    This `hook` will be used in the solids model to calculate the slip velocity between
    fluid and solid phase.

    The output variable ``U_slip`` is the slip velocity with size equal to ``n_faces`` and it
    is dimensionless.
    The ``solid_field_index`` is the index of the dispersed solid field.
    The ``layer_index`` is the index of the layer and continuous field in the layer (in which the solid
    field is dispersed).

    .. Note::
        It is important to know that the calculations for velocity is performed over the faces (see
        ``n_faces`` param). For that, any variable that should be retrieved using :cpp:func:`get_simulation_array`
        must be use value ``FACE`` in the :cpp:enum:`GridScope` param.

    :param ctx: ALFAsim's plugins context
    :param U_slip: Slip velocity between fluid and solid phase
    :param solid_field_index: Index of the dispersed solid field
    :param layer_index: Index of the Layer or Continuous Field
    :param n_faces: Number of faces.

    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_SLIP_VELOCITY(ctx, U_slip, disp_field_index, layer_index, n_faces)
        {
            const char* plugin_id = get_plugin_id()
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            // MyStruct is a developer defined struct to hold
            // all important information for plugin hooks.
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(ctx, (void**) &data, plugin_id, thread_id);
            if (errcode != OK) {
                return errcode;
            }

            // compute the slip velocity using your own correlation
            for (int i = 0; i < n_faces; ++i){
                U_slip[i] = slip_velocity[i];
            }

            return OK;
        }
    """


def calculate_relative_slurry_viscosity(
    ctx: "void*",
    mu_r: "double*",
    solid_field_index: "int",
    layer_index: "int",
    n_faces: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_RELATIVE_SLURRY_VISCOSITY(void* ctx, double* mu_r, int solid_field_index, int layer_index, int n_faces)``

    Internal `hook` to calculate the relative slurry viscosity in the Solids Model.
    This `hook` will be used in the Solids model to calculate the effective viscosity of the slurry
    (solid field + continuous field).

    The relative slurry viscosity is defined by:

    .. math::

        \\begin{equation}
            \\mu_r = \\frac{\\mu_{eff}}{\\mu_c}
        \\end{equation}


    .. rubric:: Where

    :1: :math:`\\mu_r` is the relative emulsion viscosity
    :2: :math:`\\mu_{eff}` is the effective viscosity
    :3: :math:`\\mu_c` is the viscosity of the continuous field

    The output variable ``mu_r`` is the relative slurry viscosity with size equal to ``n_faces`` and it
    is dimensionless.
    The ``solid_field_index`` is the index of the dispersed solid field.
    The ``layer_index`` is the index of the layer and continuous field in the layer (in which the solid
    field is dispersed).

    .. Note::
        It is important to know that the calculations for viscosity is performed over the faces (see
        ``n_faces`` param). For that, any variable that should be retrieved using :cpp:func:`get_simulation_array`
        must be use value ``FACE`` in the :cpp:enum:`GridScope` param.

    This `hook` allows the implementation of the relative slurry viscosity correlation. Once the plugin
    installed it is important to be selected in the solids model configuration inside the Physics data
    tree in the ALFAsim application in order to be used.

    :param ctx: ALFAsim's plugins context
    :param mu_r: Relative slurry viscosity
    :param solid_field_index: Index of the dispersed solid field
    :param layer_index: Index of the Layer or Continuous Field
    :param n_faces: Number of faces.
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_RELATIVE_SLURRY_VISCOSITY(ctx, mu_r, solid_field_index, layer_index, n_faces)
        {
            const char* plugin_id = get_plugin_id()
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            // MyStruct is a developer defined struct to hold
            // all important information for plugin hooks.
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(ctx, (void**) &data, plugin_id, thread_id);
            if (errcode != OK) {
                return errcode;
            }

            // compute the relative slurry viscosity using your own correlation
            for (int i = 0; i < n_faces; ++i){
                mu_r[i] = relative_slurry_viscosity[i];
            }

            return OK;
        }
    """


def initialize_mass_fraction_of_tracer(
    ctx: "void*", phi_initial: "void*", tracer_index: "int"
) -> "int":
    """
    **c++ signature** : ``HOOK_INITIALIZE_MASS_FRACTION_OF_TRACER(void* ctx, void* phi_initial, int tracer_index)``

    Internal tracer model Hook to initialize the mass fraction of tracer, given by `tracer_id`, in the entire
    network. The output variable `phi_initial` is the initial mass fraction of the given tracer in respect
    to the mass of the mixture.

    :param ctx: ALFAsim's plugins context
    :param phi_initial: Initial mass fraction of tracer in respect to the mass of the mixture
    :param tracer_index: Tracer ID
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_INITIALIZE_MASS_FRACTION_OF_TRACER(
            ctx, phi_initial, tracer_index)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            if (tracer_index != data.my_user_defined_tracer_id) {
                return OK;
            } else {
                // Set a initial value to the tracer mass fraction
                // phi_initial has size equal to 1
                *static_cast<double*>(phi_initial) = 0.0;
            }
            return OK;
        }

    """


def calculate_mass_fraction_of_tracer_in_phase(
    ctx: "void*",
    phi: "void*",
    phi_phase: "void*",
    tracer_index: "int",
    phase_index: "int",
    n_control_volumes: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_MASS_FRACTION_OF_TRACER_IN_PHASE(void* ctx, void* phi, void* phi_phase,
    int tracer_index, int phase_index, int n_control_volumes)``

    Internal tracer model `Hook` to calculate the mass fraction of tracer, given by ``tracer_index``, in phase,
    given by ``phase_index``. The input variable ``phi`` is the mass fraction of the given tracer in respect to
    the mass of the mixture. The output variable ``phi_phase`` is the mass fraction of the given tracer in
    respect to the mass of the given phase. Both ``phi`` and ``phi_phase`` have size equal to ``n_control_volumes``.

    :param ctx: ALFAsim's plugins context
    :param phi: Array of mass fraction of tracer in respect to the mass of the mixture
    :param phi_phase: Array of mass fraction of tracer in respect to the mass of the phase given by `phase_index`
    :param tracer_index: Tracer ID
    :param phase_index: Phase ID
    :param n_control_volumes: Number of control volumes
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_MASS_FRACTION_OF_TRACER_IN_PHASE(
            ctx, phi, phi_phase, tracer_index, phase_index, n_control_volumes)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            // Casting to double pointer
            double* phi_ptr = static_cast<double*>(phi);
            double* phi_phase_ptr = static_cast<double*>(phi_phase);
            // Check if the tracer_index was added by this plugin
            if (tracer_index != data.my_user_defined_tracer_id){
                return OK
            }
            // Let suppose that this tracer is only in the gas phase
            if(phase_index != data.gas_id) {
                 for (int i = 0; i < n_control_volumes; ++i) {
                    phi_phase_ptr[i] = 0.0;
                 }
            } else {
                // Calculate and set the Phi_phase value
                for (int i = 0; i < n_control_volumes; ++i) {
                    phi_phase_ptr[i] =
                        data.calculate_mass_fraction_of_tracer_in_gas(
                            phi_ptr[i],
                            // List of params that can be
                            // retrieved by get_simulation_array()
                            );
                }
            }
            return OK;
        }

    .. warning::
        The plugin developer must NOT change ``phi`` variable, only the output variable ``phi_phase``.

    """


def calculate_mass_fraction_of_tracer_in_field(
    ctx: "void*",
    phi_phase: "void*",
    phi_field: "void*",
    tracer_index: "int",
    field_index: "int",
    phase_index_of_field: "int",
    n_control_volumes: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_MASS_FRACTION_OF_TRACER_IN_FIELD(void* ctx, void* phi_phase, void* phi_field,
    int tracer_index, int field_index, int phase_index_of_field, int n_control_volumes)``

    Internal tracer model Hook to calculate the mass fraction of tracer, given by ``tracer_index``, in field,
    given by ``field_index``. The input variable ``phi_phase`` is the mass fraction of the given tracer in
    respect to the mass of the given phase, in which the ID is `phase_index_of_field`. The output variable
    ``phi_field`` is the mass fraction of the given tracer in respect to the mass of the given field. Both
    ``phi_phase`` and ``phi_field`` have size equal to ``n_control_volumes``.

    :param ctx: ALFAsim's plugins context
    :param phi_phase: Array of mass fraction of tracer in respect to the mass of the phase given by `phase_index_of_field`
    :param phi_field: Array of mass fraction of tracer in respect to the mass of the field given by `field_index`
    :param tracer_index: Tracer ID
    :param field_index: Field ID
    :param phase_index_of_field: Phase ID of field
    :param n_control_volumes: Number of control volumes
    :returns: Return OK if successful or anything different if failed

     Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_MASS_FRACTION_OF_TRACER_IN_FIELD(
            ctx, phi_phase, phi_field, tracer_index, field_index,
            phase_index_of_field, n_control_volumes)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            // Casting to double pointer
            double* phi_phase_ptr = static_cast<double*>(phi_phase);
            double* phi_field_ptr = static_cast<double*>(phi_field);
            // Check if the tracer_index was added by this plugin
            if (tracer_index != data.my_user_defined_tracer_id){
                return OK
            }
            // Let suppose that this tracer is only in the gas phase
            if(phase_index_of_field != data.gas_phase_id) {
                 for (int i = 0; i < n_control_volumes; ++i) {
                    phi_field_ptr[i] = 0.0;
                 }
            } else {
                // Calculate and set the Phi_field value
                for (int i = 0; i < n_control_volumes; ++i) {
                    phi_field_ptr[i] =
                        data.mass_fraction_of_tracer_in_gas_fields(
                            phi_phase_ptr[i],
                            // List of params that can be
                            // retrieved by get_simulation_array()
                            );
                }
            }
            return OK;
        }

    .. warning::
        The plugin developer must NOT change ``phi_phase`` variable, only the output variable ``phi_field``.

    """


def set_prescribed_boundary_condition_of_mass_fraction_of_tracer(
    ctx: "void*", phi_presc: "void*", tracer_index: "int"
) -> "int":
    """
    **c++ signature** : ``HOOK_SET_PRESCRIBED_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER(void* ctx, void* phi_presc,
    int tracer_index)``

    Internal tracer model `hook` to set the initial prescribed boundary condition of mass fraction of tracer,
    given by ``tracer_index``. The output variable ``phi_presc`` is the prescribed mass fraction of the given tracer
    in respect to the mass of the mixture. Note that all boundary nodes will be populated with ``phi_presc`` value
    set by this `hook`.

    Please note that this `hook` sets the first mass fraction related boundary conditions value to
    the user defined tracer. However the hook :py:func:`HOOK_UPDATE_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER<alfasim_sdk._internal.hook_specs.update_boundary_condition_of_mass_fraction_of_tracer>`
    allows the plugin developer to update this value.

    :param ctx: ALFAsim's plugins context
    :param phi_presc: Prescribed mass fraction of tracer
    :param tracer_index: Tracer ID
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_SET_PRESCRIBED_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER(
            ctx, phi_presc, tracer_index)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            if (tracer_index != data.my_user_defined_tracer_id) {
                return OK;
            } else {
                // Set a initial boundary condition
                // to the tracer mass fraction.
                // phi_presc has size equal to 1.
                *static_cast<double*>(phi_presc) = 0.0;
            }
            return OK;
        }

    """


def update_boundary_condition_of_mass_fraction_of_tracer(
    ctx: "void*",
    phi_presc: "void*",
    tracer_index: "int",
    vol_frac_bound: "void*",
    n_fields: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_UPDATE_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER(void* ctx, void* phi_presc,
    void* phi_field, int tracer_index, void* vol_frac_bound, int n_fields)``

    Internal tracer model `hook` to update the prescribed mass fraction of tracer, given by ``tracer_id``.
    The output variable ``phi_presc`` is the prescribed mass fraction of the given tracer in respect to
    the mass of the mixture. The ``vol_frac_bound`` is the volume fraction of fields at the boundary in which
    the ``phi_presc`` is being calculated.

    This `hook` allows the developer to update the boundary conditions of mass fraction that may depend on |alfasim|'s
    internal variables that may change during the simulation. So, this update will be performed to each time step.

    :param ctx: ALFAsim's plugins context
    :param phi_presc: Prescribed mass fraction of tracer
    :param tracer_index: Tracer ID
    :param vol_frac_bound: Volume fraction of fields in the boundary
    :param n_fields: Number of fields
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_UPDATE_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER(
            ctx, phi_presc, tracer_index)
        {
            // getting plugin internal data
            int errcode = -1;
            int thread_id = -1;
            errcode = alfasim_sdk_api.get_thread_id(ctx, &thread_id);
            if (errcode != OK) {
                return errcode;
            }
            MyStruct* data = nullptr;
            errcode = alfasim_sdk_api.get_plugin_data(
                    ctx, (void**) &data, plugin_id, thread_id);
            // Casting to double pointer
            double* phi_presc_ptr = static_cast<double*>(phi_presc);
            double* vol_frac_bound_ptr = static_cast<double*>(vol_frac_bound);
            // Let suppose that this tracer is only in the gas field
            if (tracer_index != data.my_user_defined_tracer_id) {
                return OK;
            } else {
                // Update the boundary condition
                // to the tracer mass fraction.
                phi_presc_ptr =
                        data.calc_bc_mass_fraction_of_tracer_in_gas_field(
                            vol_frac_bound_ptr[data.continuous_gas_field_id],
                            // List of params that can be
                            // retrieved by get_simulation_array()
                            );
            }
            return OK;
        }

    .. warning::
        The plugin developer must NOT change ``vol_frac_bound`` variable, only the output variable ``phi_presc``.

    """


def calculate_ucm_friction_factor_stratified(
    ctx: "void*", ff_wG: "double*", ff_wL: "double*", ff_i: "double*"
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_UCM_FRICTION_FACTOR_STRATIFIED(void* ctx, double* ff_wG, double* ff_wL,
    double* ff_i)``

    Internal unit cell model `hook` to calculate the wall and interfacial friction factors for stratified
    fluid flow pattern. The unit cell model represents a two phase flow with Gas and Liquid Phases.
    The output variables ``ff_wG``, ``ff_wL`` and ``ff_i`` are the Gas-Wall friction factor, Liquid-Wall
    friction factor and interfacial Gas-Liquid friction factor, respectively.

    This `hook` allows the developer to implement your own correlation for friction factor in a stratified
    flow.

    :param ctx: ALFAsim's plugins context
    :param ff_wG: Gas-Wall Friction Factor
    :param ff_wL: Liquid-Wall Friction Factor
    :param ff_i: Interfacial Gas-Liquid Friction Factor
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_UCM_FRICTION_FACTOR_STRATIFIED(ctx, ff_wG, ff_wL, ff_i)
        {
            int errcode = -1;
            int G = TwoPhaseSystem::GAS;
            int L = TwoPhaseSystem::LIQUID;

            // Getting friction factor input data from context
            double alpha[2];
            errcode = alfasim_sdk_api.get_ucm_friction_factor_input_variable(
                ctx, &alpha[G], "alpha", TwoPhaseSystem::GAS);
            if (errcode != OK){ return errcode; }
            errcode = alfasim_sdk_api.get_ucm_friction_factor_input_variable(
                ctx, &alpha[L], "alpha", TwoPhaseSystem::LIQUID);
            if (errcode != OK){ return errcode; }
            // And so on to each friction factor input variable
            // U(velocities), rho(densities), mu(viscosities) and D(pipe diameter)

             // Getting the fluid geometrical properties
            double S_w[2];
            double S_i;
            double H[2];
            errcode = alfasim_sdk_api.get_ucm_fluid_geometrical_properties(
                ctx, S_w, &S_i, H, alpha[G], D);
            if (errcode != OK){ return errcode; }

            // Compute the friction factors using your own correlation.
            // Also, using the variables: alpha, U, rho, mu, D, S_w, S_i and H

            *ff_wG = gas_wall_ff;
            *ff_wL = liq_wall_ff;
            *ff_i = gas_liq_ff;

            return OK;
        }
    """


def calculate_ucm_friction_factor_annular(
    ctx: "void*", ff_wG: "double*", ff_wL: "double*", ff_i: "double*"
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_UCM_FRICTION_FACTOR_ANNULAR(void* ctx, double* ff_wG, double* ff_wL,
    double* ff_i)``

    Internal unit cell model `hook` to calculate the wall and interfacial friction factors for annular
    fluid flow pattern. The unit cell model represents a two phase flow with Gas and Liquid Phases.
    The output variables ``ff_wG``, ``ff_wL`` and ``ff_i`` are the Gas-Wall friction factor, Liquid-Wall
    friction factor and interfacial Gas-Liquid friction factor, respectively.

    This `hook` allows the developer to implement your own correlation for friction factor in a annular
    flow.

    :param ctx: ALFAsim's plugins context
    :param ff_wG: Gas-Wall Friction Factor
    :param ff_wL: Liquid-Wall Friction Factor
    :param ff_i: Interfacial Gas-Liquid Friction Factor
    :returns: Return OK if successful or anything different if failed

    Example of usage:
        The same example presented in :py:func:`HOOK_CALCULATE_UCM_FRICTION_FACTOR_STRATIFIED<alfasim_sdk._internal.hook_specs.calculate_ucm_friction_factor_stratified>`
        can be used, just change the `hook` name to `HOOK_CALCULATE_UCM_FRICTION_FACTOR_ANNULAR`.
    """


def calculate_liq_liq_flow_pattern(
    ctx: "void*", ll_fp: "int*", water_vol_frac: "double*"
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_LIQ_LIQ_FLOW_PATTERN(void* ctx, int* ll_fp, double* water_vol_frac)``

    Internal `hook` to calculate the liquid-liquid flow pattern (Oil-Water) and the water volume fraction
    in the Liquid-Liquid system. The Liquid-Liquid system is a two phase flow with Oil and Water Phases.
    It represents the separation of Liquid phase (into oil and water phases) used in the two phase system
    (Gas-Liquid). The output variables ``ll_fp`` and ``water_vol_frac`` are the liquid-liquid flow pattern
    and volume fraction of water, respectively.

    .. note::
        The main input variables needed to estimate the flow pattern is available in the API function
        :cpp:func:`get_liq_liq_flow_pattern_input_variable`. Note that, the variables listed in the documentation
        of the cited function are related to one control volume, in which the estimation is applied.

    This `hook` allows the developer to implement your own flow pattern estimation algorithm for the liquid-liquid
    system.

    The ``ll_fp`` must be one of the following values: |br|
    - `0 - Unknown`: Unknown Flow Pattern. |br|
    - `1 - Ambivalent`: Ambivalent Flow Pattern between Dispersed Oil and Dispersed Water. |br|
    - `2 - Dispersed Oil`: Dispersed oil in continuous water. |br|
    - `3 - Dispersed Water`: Dispersed water in continuous Oil. |br|
    - `4 - Separated`: Separated continuous oil and continuous water. |br|
    - `5 - Separated Wavy`: Separated with waves. |br|
    - `6 - Separated Mixed`: Separated with dispersed oil and water droplets. |br|

    Any value different from these values will be assumed an `Unknown` flow pattern.

    :param ctx: ALFAsim's plugins context
    :param ll_fp: Liquid-Liquid Flow Pattern
    :param water_vol_frac: Volume fraction of water in the Liquid-Liquid System
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_LIQ_LIQ_FLOW_PATTERN(ctx, ll_fp, water_vol_frac)
        {
            int errcode = -1;
            int O = LiquidLiquidSystem::OIL;
            int W = LiquidLiquidSystem::WATER;

            // Getting liq-liq Flow Pattern input data from context
            double rho[2];
            errcode = alfasim_sdk_api.get_liq_liq_flow_pattern_input_variable(
                ctx, &rho[O], "rho", LiquidLiquidSystem::OIL);
            if (errcode != OK){ return errcode; }
            errcode = alfasim_sdk_api.get_liq_liq_flow_pattern_input_variable(
                ctx, &rho[W], "rho", LiquidLiquidSystem::WATER);
            if (errcode != OK){ return errcode; }
            // And so on to each input variable
            // U_S(superficial velocities), mu(viscosities)
            // and D_h(liquid hydraulic diameter)

            // Estimate the liquid-liquid Flow pattern and volume fraction of water
            // using your own algorithm.

            *ll_fp = flow_pattern;
            *water_vol_frac = alpha_W;

            return OK;
        }
    """


def calculate_liquid_effective_viscosity(
    ctx: "void*", mu_l_eff: "double*", ll_fp: "int"
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_LIQUID_EFFECTIVE_VISCOSITY(void* ctx, double* mu_l_eff, int ll_fp)``

    Internal `hook` to calculate the liquid (Oil-Water) effective viscosity in the Liquid-Liquid system.
    It represents viscosity of a Liquid phase used in the two phase system (Gas-Liquid).
    The output variable ``mu_l_eff`` is the Liquid Effective Viscosity. It has unit equal to ``[Pa.s]``.

    .. note::
        The main input variables needed to estimate the liquid effective viscosity is available in the API function
        :cpp:func:`get_liquid_effective_viscosity_input_variable`. Note that, the variables listed in the
        documentation of the cited function are related to one control volume, in which the estimation is applied.

    This `hook` allows the developer to implement your own liquid effective viscosity correlation to
    represent the viscosity of an unified liquid phase that represents the Oil-Water mixture.

    :param ctx: ALFAsim's plugins context
    :param mu_l_eff: Liquid Effective Viscosity
    :param ll_fp: Liquid-Liquid Flow Pattern (see :py:func:`HOOK_CALCULATE_LIQ_LIQ_FLOW_PATTERN<alfasim_sdk._internal.hook_specs.calculate_liq_liq_flow_pattern>` for possible values)
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_LIQUID_EFFECTIVE_VISCOSITY(ctx, mu_l_eff, ll_fp)
        {
            int errcode = -1;
            int O = LiquidLiquidSystem::OIL;
            int W = LiquidLiquidSystem::WATER;

            // Getting liquid Effective Viscosity input data from context
            double rho[2];
            errcode = alfasim_sdk_api.get_liquid_effecticve_viscosity_input_variable(
                ctx, &rho[O], "rho", LiquidLiquidSystem::OIL);
            if (errcode != OK){ return errcode; }
            errcode = alfasim_sdk_api.get_liquid_effecticve_viscosity_input_variable(
                ctx, &rho[W], "rho", LiquidLiquidSystem::WATER);
            if (errcode != OK){ return errcode; }
            // And so on to each input variable
            // U_S(superficial velocities), mu(viscosities for Oil and Water) and
            // D_h(liquid hydraulic diameter)

            // Estimate the liquid effective viscosity using your own algorithm.
            // Since the liquid effective viscosity depends on Liquid-Liquid Flow Pattern,
            // it is provide as an Hook parameter (`ll_fp`).

            *mu_l_eff = liquid_viscosity;

            return OK;
        }
    """


def calculate_gas_liq_surface_tension(
    ctx: "void*", sigma_gl: "double*", ll_fp: "int"
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_GAS_LIQ_SURFACE_TENSION(void* ctx, double* sigma_gl, int ll_fp)``

    Internal `hook` to calculate the Gas-liquid Surface Tension based in the Liquid-Liquid System.
    It represents Gas-Liquid surface tension used in the two phase system (Gas-Liquid).
    The output variable ``sigma_gl`` is the Gas-Liquid Surface tension. It has unit equal to ``[N/m]``.

    .. note::
        The main input variables needed to estimate the Gas-Liquid Surface Tension is available in the API function
        :cpp:func:`get_gas_liq_surface_tension_input_variable`. Note that, the variables listed in the
        documentation of the cited function are related to one control volume, in which the estimation is applied.

    This `hook` allows the developer to implement your own Gas-liquid Surface Tension correlation for
    an unified liquid phase that represents the Oil-Water mixture.

    .. note::
        It is important to note that the Gas-Liquid Surface tension depends on Gas-Oil and Gas-Water
        Surface Tensions from Liquid-Liquid system. Since it depends on the Liquid-Liquid Flow pattern,
        the Gas-Liquid Surface Tension must take it into account.

    :param ctx: ALFAsim's plugins context
    :param sigma_gl: Gas-Liquid Surface Tension
    :param ll_fp: Liquid-Liquid Flow Pattern (see :py:func:`HOOK_CALCULATE_LIQ_LIQ_FLOW_PATTERN<alfasim_sdk._internal.hook_specs.calculate_liq_liq_flow_pattern>` for possible values)
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_GAS_LIQ_SURFACE_TENSION(ctx, sigma_gl, ll_fp)
        {
            int errcode = -1;
            int O = LiquidLiquidSystem::OIL;
            int W = LiquidLiquidSystem::WATER;

            // Getting liquid Effective Viscosity input data from context
            double sigma_gll[2];
            errcode = alfasim_sdk_api.get_gas_liq_surface_tension_input_variable(
                ctx, &sigma_gll[O], "sigma_gll", LiquidLiquidSystem::OIL);
            if (errcode != OK){ return errcode; }
            // And so on to each input variable
            // sigma_gw(Surface tension Gas-Water) and alpha_w(Water Volume Fraction)

            // Estimate the Gas-Liquid Surface Tension using your own algorithm.
            // Since the Gas-Liquid Surface Tension depends on Liquid-Liquid Flow Pattern,
            // it is provide as an Hook parameter (`ll_fp`).

            *sigma_gl = gas_liq_sigma;

            return OK;
        }
    """


def calculate_liq_liq_shear_force_per_volume(
    ctx: "void*",
    shear_w: "double*",
    shear_i: "double*",
    u_fields: "double*",
    vol_frac_fields: "double*",
    ll_fp: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_LIQ_LIQ_SHEAR_FORCE_PER_VOLUME(void* ctx, double* shear_w,
    double* shear_i, double* u_fields, double* vol_frac_fields, int ll_fp)``

    Internal `hook` to calculate the Shear Force per unit volume for the Liquid-Liquid System.
    Also Field velocities and field volume fraction must be calculated.
    It is important to compute the shear stress term in the momentum equation for the Liquid-Liquid System.

    .. note::
        The main input variables needed to estimate the Shear Force is available in the API function
        :cpp:func:`get_liq_liq_shear_force_per_volume_input_variable`. Note that, the variables listed in the
        documentation of the cited function are related to one control volume, in which the estimation is applied.

    The output variable ``shear_w`` is the Wall Shear Force per unit Volume with size equal to ``2``
    (for Oil and Water phases) and it has unit equal to ``[N/m^3]``.
    The output variable ``shear_i`` is the Interfacial Shear Force per unit Volume between Oil and Water
    phases it has unit equal to ``[N/m^3]``.
    The output variable ``u_fields`` is the field velocities with size ``4`` because values for continuous
    fields (Oil and Water) and for dispersed fields (Oil Droplet in Water and Water Droplet in Oil) must be
    provided and it has unit equal to ``[m/s]``.
    The output variable ``vol_frac_fields`` is the field volume fractions also with size ``4``, just like
    ``u_fields`` and it has unit equal to ``[kg of field/ kg of liquid-liquid mixture]``.

    .. Note::
        The outputs ``u_fields`` and ``vol_frac_fields`` are vectors in which the order of the fields are
        Oil Continuous(``O``) for index 0, Water Continuous(``W``) for index 1, Oil Droplet in Water(``OW``)
        for index 3 and Water Droplets in Oil(``WO``) for index 4. See the example below.

    This `hook` allows the implementation of the shear force for the Liquid-Liquid System,an important
    output of the Unit Cell Model. Since this kind of calculation depends on Liquid-Liquid Flow
    Pattern, it is provided as an hook parameter.

    :param ctx: ALFAsim's plugins context
    :param shear_w: Wall Shear Force per unit Volume
    :param shear_i: Interfacial (Oil-Water) Shear Force per unit Volume
    :param u_fields: Field Velocities
    :param vol_frac_fields: Field Voluem Fraction
    :param ll_fp: Liquid-Liquid Flow Pattern (see :py:func:`HOOK_CALCULATE_LIQ_LIQ_FLOW_PATTERN<alfasim_sdk._internal.hook_specs.calculate_liq_liq_flow_pattern>` for possible values)
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_LIQ_LIQ_SHEAR_FORCE_PER_VOLUME(ctx, shear_w,
            shear_i, U_fields, vol_frac_fields, ll_fp)
        {
            int errcode = -1;
            int O = 0;
            int W = 1;
            int OW = 2;
            int WO = 3;

            // Getting shear term input data from context
            double rho[2];
            errcode = alfasim_sdk_api.get_liq_liq_shear_force_per_volume_input_variable(
                ctx, &rho[O], "rho", LiquidLiquidSystem::OIL);
            if (errcode != OK){ return errcode; }
            errcode = alfasim_sdk_api.get_liq_liq_shear_force_per_volume_input_variable(
                ctx, &rho[W], "rho", LiquidLiquidSystem::WATER);
            if (errcode != OK){ return errcode; }
            // And so on to each input variable
            // U_S(superficial velocities), mu(viscosities for Oil and Water) and
            // D_h(liquid hydraulic diameter)

            // Calculate the wall and interfacial shear force per unit volume, fields (Liquid-Liquid System)
            // velocities and fields (Liquid-Liquid System) volume fraction using your own algorithm.

            shear_w[O] = wall_shear_force[O];
            shear_w[W] = wall_shear_force[W];
            *shear_i = interfacial_shear_force;
            u_fields[O] = U[O];
            u_fields[W] = U[W];
            u_fields[OW] = U[OW];
            u_fields[WO] = U[WO];
            vol_frac_fields[O] = alpha[O];
            vol_frac_fields[W] = alpha[W];
            vol_frac_fields[OW] = alpha[OW];
            vol_frac_fields[WO] = alpha[WO];

            return OK;
        }
    """


def calculate_relative_emulsion_viscosity(
    ctx: "void*",
    mu_r: "double*",
    mu_disp: "double",
    mu_cont: "double",
    alpha_disp_in_layer: "double",
    disp_field_index: "int",
    cont_field_index: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_RELATIVE_EMULSION_VISCOSITY(void* ctx, double* mu_r, double mu_disp, double mu_cont, double alpha_disp_in_layer)``

    Internal `hook` to calculate the relative emulsion viscosity in the Emulsion Model.
    This `hook` will be used in the emulsion model to calculate the apparent viscosity of the emulsion
    (Continuous field + dispersed field = layer).

    The relative emulsion viscosity is defined by:

    .. math::

        \\begin{equation}
            \\mu_r = \\frac{\\mu_m}{\\mu_c}
        \\end{equation}


    .. rubric:: Where

    :1: :math:`\\mu_r` is the relative emulsion viscosity
    :2: :math:`\\mu_m` is the apparent viscosity
    :3: :math:`\\mu_c` is the viscosity of the continuous field

    The output variable ``mu_r`` is the relative emulsion viscosity, ``mu_disp`` is the dispersed field
    viscosity, ``mu_cont`` is the continuous field viscosity and ``alpha_disp_in_layer`` is the volume
    fraction of dispersed field in the layer. Finally ``disp_field_index`` and ``cont_field_index`` are
    the Dispersed and Continuous Field indexes of the emulsion, respectively.

    This `hook` allows the implementation of the relative emulsion viscosity correlation. Once the plugin
    installed it is important to be selected in the emulsion model configuration inside the Physics data
    tree in the ALFAsim application in order to be used.

    :param ctx: ALFAsim's plugins context
    :param mu_r: Relative emulsion viscosity
    :param mu_disp: Dispersed field viscosity
    :param mu_cont: Continuous field viscosity
    :param alpha_disp_in_layer: Volume fraction of dispersed field in layer.
    :param disp_field_index: Index of the dispersed field
    :param cont_field_index: Index of the continuous field

    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_RELATIVE_EMULSION_VISCOSITY(ctx, mu_r, mu_disp, mu_cont, alpha_disp_in_layer)
        {
            int water_in_oil_id = -1;
            errcode = alfasim_sdk_api.get_field_id(ctx, &water_in_oil_id, "water in oil");
            if (errcode != OK) {
                return errcode;
            }

            int oil_in_water_id = -1;
            errcode = alfasim_sdk_api.get_field_id(ctx, &oil_in_water_id, "oil in water");
            if (errcode != OK) {
                return errcode;
            }

            if (disp_field_index == oil_in_water_id){
                // Calculate the relative emulsion viscosity
                // for water dominated scenario.
                // ComputeForWaterDominated is a function implemented
                // by plugin developer
                ComputeForWaterDominated(mu_r, mu_disp, mu_cont);
            } else if (disp_field_index == water_in_oil_id){
                // Calculate the relative emulsion viscosity
                // for oil dominated scenario
                // ComputeForOilDominated is a function implemented
                // by plugin developer
                ComputeForOilDominated(mu_r, n_faces);
            }

            return OK;
        }
    """


def friction_factor(v1: "int", v2: "int") -> "int":
    """
    Docs for Friction Factor
    """


def env_temperature(v3: "float", v4: "float") -> "float":
    """
    Docs for Environment Temperature
    """


def calculate_entrained_liquid_fraction(
    U_S: "const double[2]",
    rho: "const double[2]",
    mu: "const double[2]",
    sigma: "double",
    D: "double",
    theta: "double",
) -> "double":
    """
    Hook for droplet entrainment model when in annular flow (in unit cell model)

    :param U_S: Gas and liquid superficial velocities [m/s]
    :param rho: Phase densities [kg/m3]
    :param mu: Phase viscosities [Pa.s]
    :param sigma: Surface tension [N.m]
    :param D: Pipe diameter [m]
    :param theta: Pipe inclination [rad]

    :returns:
        Entrainment fraction, defined as the ratio between the droplet mass flow rate and the total liquid
        mass flow rate (dimensionless)
    """


def update_internal_deposition_layer(
    ctx: "void*",
    thickness: "void*",
    density: "void*",
    heat_capacity: "void*",
    thermal_conductivity: "void*",
    n_control_volumes: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_UPDATE_INTERNAL_DEPOSITION_LAYER(void* ctx, void* thickness, void* density, void* heat_capacity, void* thermal_conductivity,
    int n_control_volumes)``

    Internal simulator hook to evaluate the thickness and thermal properties of the deposited layer at the inside of the pipeline walls.
    This is called for accounting the diameter reduction and wall thermal effects.

    The plugin is supposed to change the given ``thickness``, ``density``, ``heat_capacity``, ``thermal_conductivity`` array pointers. Its values are contiguous
    in memory and the dimension is given by ``n_control_volumes``. It has unit equal to ``[m]``.

    :param ctx: ALFAsim's plugins context
    :param thickness: Thickness of the internal deposit layer
    :param density: Density of the internal deposit layer [kg/m3]
    :param heat_capacity: Heat capacity of the internal deposit layer [J/(kg.K)]
    :param thermal_conductivity: Thermal conductivity of the internal deposit layer [W/(m.K)]
    :param n_control_volumes: Number of control volumes
    :returns: Return OK if successful or anything different if failed

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_UPDATE_INTERNAL_DEPOSITION_LAYER(
            ctx, thickness, density, heat_capacity, thermal_conductivity, n_control_volumes)
        {
            auto errcode = -1;

            double dt = -1.0;
            errcode = alfasim.get_simulation_quantity(
                ctx, &dt, TimestepScope::CURRENT, (char*) "dt");
            if (errcode != 0) {
                return errcode;
            }

            // Handle first time step, because you won't have the previously information
            double current_time = -1.0;
            errcode = alfasim.get_simulation_quantity(
                ctx, &current_time, TimestepScope::CURRENT, (char*) "time");
            if (errcode != 0) {
                return errcode;
            }

            double wax_density = 900.0 // [kg/m3]
            double wax_heat_capacity = 2140.0 // [J/(kg.K)]
            double wax_thermal_conductivity = 0.25 // [W/(m.K)]

            if (current_time == 0.0){
                // Set a value for the deposition layer thickness
                 for (int i = 0; i < n_control_volumes; ++i) {
                   (double*) thickness[i] = 0.0; // [m]
                   (double*) density[i] = wax_density; // [kg/m3]
                   (double*) heat_capacity[i] = wax_heat_capacity; //  [J/(kg.K)]
                   (double*) thermal_conductivity[i] = wax_thermal_conductivity; // [W/(m.K)]
                }
            } else{
                // Get previously deposition layer thickness to obtain the current
                void* thickness_old_raw_ptr;
                errcode = alfasim.get_plugin_variable(
                    ctx,
                    &thickness_old_raw_ptr,
                    "thickness",
                    0,
                    TimestepScope::PREVIOUS,
                    &size);
                if (errcode != 0) {
                    return errcode;
                }
                auto* thickness_old =
                    (double*) (thickness_old_raw_ptr);

                // Calculate the variation of the deposition layer in one time step
                double* d_deposit_layer_dt = 0.0001; // [m/s]

                // Sum this variation with the thickness of the older time step
                for (int i = 0; i < n_control_volumes; ++i) {
                    (double*) thickness[i] =
                        thickness_old[i] + d_deposit_layer_dt * dt; // [m]
                   (double*) density[i] = wax_density; // [kg/m3]
                   (double*) heat_capacity[i] = wax_heat_capacity; //  [J/(kg.K)]
                   (double*) thermal_conductivity[i] = wax_thermal_conductivity; // [W/(m.K)]
                }
            }

            return OK;
        }

    In the example above is shown how to manage the ``thickness``, ``density``, ``heat_capacity``
    and ``thermal_conductivity`` arrays for each control volume. Note that the ``thickness`` should
    be always the total value for that time step, so the first time step should be handle in a
    separately way, since there is no previously information.
    """


specs = HookSpecs(
    project_name="ALFAsim",
    version="1",
    pyd_name="_alfasim_hooks",
    hooks=[
        initialize,
        finalize,
        # Update secondary variables registered by plugin
        update_plugins_secondary_variables_on_first_timestep,
        update_plugins_secondary_variables,
        update_plugins_secondary_variables_on_tracer_solver,
        # Calculate source terms
        calculate_mass_source_term,
        calculate_momentum_source_term,
        calculate_energy_source_term,
        calculate_tracer_source_term,
        # State variables calculation of phases added by plugin
        initialize_state_variables_calculator,
        finalize_state_variables_calculator,
        calculate_state_variable,
        calculate_phase_pair_state_variable,
        # Hooks related to solids phases
        initialize_particle_diameter_of_solids_fields,
        update_particle_diameter_of_solids_fields,
        # Hooks related to Solids Model
        calculate_slip_velocity,
        calculate_relative_slurry_viscosity,
        # Hooks related to Tracer added by plugin
        initialize_mass_fraction_of_tracer,
        calculate_mass_fraction_of_tracer_in_phase,
        calculate_mass_fraction_of_tracer_in_field,
        set_prescribed_boundary_condition_of_mass_fraction_of_tracer,
        update_boundary_condition_of_mass_fraction_of_tracer,
        # Hooks related to UCM Friction Factor
        calculate_ucm_friction_factor_stratified,
        calculate_ucm_friction_factor_annular,
        # Hooks related to Liquiq-Liquid Mechanistic Model
        calculate_liq_liq_flow_pattern,
        calculate_liquid_effective_viscosity,
        calculate_gas_liq_surface_tension,
        calculate_liq_liq_shear_force_per_volume,
        # Hooks related to Emulsion Model
        calculate_relative_emulsion_viscosity,
        # Extra Hooks (For testing)
        friction_factor,
        env_temperature,
        calculate_entrained_liquid_fraction,
        update_internal_deposition_layer,
    ],
)
