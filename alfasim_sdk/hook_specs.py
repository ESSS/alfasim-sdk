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
            int errcode = alfasim.get_number_of_threads(ctx, &n_threads);
            f (errcode != 0){ // or errcode != OK
                return errcode;
            }
            const char* plugin_id = get_plugin_id();
            // Plugin internal data
            for (int thread_id = 0; thread_id < n_threads; ++thread_id) {
                void* data = nullptr;
                errcode = alfasim.get_plugin_data(
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
            int liq_id = -1;
            errcode = alfasim_sdk_api.get_field_id(
                ctx, &oil_id, "oil");
            // Convertion from void* to double* and getting the
            // array range related to oil field
            double* oil_mass_source =
                (double*) mass_source + n_control_volumes * liq_id;
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
    n_control_volumes: "int",
    n_layers: "int",
) -> "int":
    """
    **c++ signature** : ``HOOK_INITIALIZE_STATE_VARIABLES_CALCULATOR(void* ctx, void* P, void* T, void* T_mix,
    int n_control_volumes, int n_layers)``

    Hook for the state variables calculator initialization (internal ``ALFAsim`` structure).

    At this point, it is possible to pre-calculate and cache any relevant information. Then, for each state variable of
    the phases in the python configuration file, the `hook` :py:func:`HOOK_CALCULATE_STATE_VARIABLE<alfasim_sdk.hook_specs.calculate_state_variables>`
    is called and return the pre-calculated values.

    :param ctx: ALFAsim's plugins context
    :param P: Pressure values array
    :param T: Temperature values array
    :param T_mix: Mixture temperature values array
    :param n_control_volumes: Number of control volumes
    :param n_layers: Number of layers
    :returns: Return OK if successful or anything different if failed

    The ``P`` and ``T_mix`` have size equal to ``n_control_volumes``. However, ``T`` has values contiguous in memory
    and its dimensions are given by ``n_layers`` and ``n_control_volumes``

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_INITIALIZE_STATE_VARIABLES_CALCULATOR(
            void* ctx, void* P, void* T, void* T_mix,
            int n_control_volumes, int n_layers)
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
            void* ctx, void* P, void* T, int n_control_volumes, i
            nt n_layers, int phase_id, int property_id, void* output)
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
    property_id: "int",
    output: "void*",
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_STATE_VARIABLE(void* ctx, void* P, void* T, int n_control_volumes, int n_layers,
    int phase_id, int property_id, void* output)``

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
    :param n_layers: Number of layers
    :param n_phase_id: Id of phase in which the property must be calculated
    :param property_id: A :cpp:enum:`StateVariable` value. It indicates which
                        property must be calculated
    :param output: Output values array
    :returns: Return OK if successful or anything different if failed

    The ``output`` parameter must be filled with the calculated property for each control volume. The
    pressure ``P`` and layer or mixture temperature ``T`` (Depending on the energy model being used)
    are given in order to perform the calculation. The number of control volumes is also given for
    convenience.

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_STATE_VARIABLE(
            void* ctx, void* P, void* T,
            int n_control_volumes, int n_layers,
            int phase_id, int property_id, void* output)
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
    property_id: "int",
    output: "void*",
) -> "int":
    """
    **c++ signature** : ``HOOK_CALCULATE_PHASE_PAIR_STATE_VARIABLE(void* ctx, void* P, void* T_mix, int n_control_volumes,
    int phase1_id, int phase2_id, int property_id, void* output)``

    Hook to calculate the state variable given by the `property_id` (See :cpp:enum:StateVariable values), for the phase
    pair `(phase1_id, phase2_id)` (Note that the phase id is the same as the one retrieved from the :py:func:`get_phase_id()`
    API function - It is not advisable to use hardcoded numbers).

    List of affected variables:|br|
    - ``Interfacial Tension``

    :param ctx: ALFAsim's plugins context
    :param P: Pressure values array
    :param T_mix: Mixture temperature values array
    :param n_control_volumes: Number of control volumes
    :param n_phase1_id: Id of phase one in which the property must be calculated
    :param n_phase2_id: Id of phase two in which the property must be calculated
    :param property_id: A :cpp:enum:`StateVariable` value. It indicates which
                        property must be calculated
    :param output: Output values array
    :returns: Return OK if successful or anything different if failed

    The output parameter must be filled with the calculated property for each control volume. The
    pressure ``P`` and mixture temperature ``T_mix`` are given in order to perform the calculation.
    The number of control volumes is also given for convenience.

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_CALCULATE_PHASE_PAIR_STATE_VARIABLE(
            void* ctx, void* P, void* T_mix, int n_control_volumes,
            int phase1_id, int phase2_id, int property_id, void* output)
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
    The plugin developer should free/delete any allocated data from the :py:func:`HOOK_INITIALIZE_STATE_VARIABLE_CALCULATOR<alfasim_sdk.hook_specs.initialize_state_variables_calculator>`.

    :param ctx: ALFAsim's plugins context
    :returns: Return OK if successful or anything different if failed

    If there is no need memory deallocation a minimal implementation would be:

    Example of usage:

    .. code-block:: c++
        :linenos:
        :emphasize-lines: 1

        HOOK_FINALIZE_STATE_VARIABLES_CALCULATOR(void* ctx)
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
    :py:func:`HOOK_UPDATE_PLUGIN_SECONDARY_VARIABLES_ON_FIRST_TIMESTEP<alfasim_sdk.hook_specs.update_plugins_secondary_variables_on_first_timestep>`,
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
            void* ctx, void* particle_diameter,
            int n_control_volumes, int solids_field_id)
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
                    output[i] = data.constant_particle_size;
                    // The value is calculated
                    // MyStruct has a function
                    // called 'initial_particle_size()'
                    output[i] = data.initial_particle_size(
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
            void* ctx, void* particle_diameter,
            int n_control_volumes, int solids_field_id)
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
                    output[i] = data.constant_particle_size;
                    // The value is calculated
                    // MyStruct has a function
                    // called 'compute_particle_size()'
                    output[i] = data.compute_particle_size(
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
    U_fields: "void*",
    alpha_f: "void*",
    d_disp_fields: "void*",
    P: "void*",
    rho_f: "void*",
    mu_f: "void*",
    sin_theta_f: "void*",
    delta_x_f: "void*",
) -> "int":
    """
    Internal simulator hook to calculate slip velocity between fluids
    and solid phase.

    :param ctx: ALFAsim's plugins context
    :param U_fields: Field velocities,
    :param alpha_f: Field Volume fractions on faces,
    :param d_disp_fields: Diameter of dispersed fields,
    :param P: Pressure,
    :param rho_f: Field densities on faces,
    :param mu_f: Field viscosities on faces,
    :param sin_theta_f: Sin of Theta on faces in which Theta is the angle between the Pipe and the Y-Axis,
    :param delta_x_f: The control volume lenght related to the faces,

    :returns: Return OK if successful or anything different if failed

    It is expected to be changed the U_fields of solid phase, whose index will be available via API.
    """


def calculate_slurry_viscosity(
    ctx: "void*", alpha_f: "void*", mu_f: "void*", mu_f_layer: "void*"
) -> "int":
    """
    Internal simulator hook to calculate slurry viscosity of layer(s).

    :param ctx: ALFAsim's plugins context
    :param alpha_f: Fields Volume fractions on faces,
    :param mu_f: Field viscosities on faces,
    :param mu_f_layer: Layer Viscosities on faces,

    :returns: Return OK if successful or anything different if failed

    It is expected to be changed the mu_f_layer of oil layer(continuous oil and dispersed solid),
    whose index will be available via API.
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
            void* ctx, void* phi_initial, int tracer_index)
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
            void* ctx, void* phi, void* phi_phase,
            int tracer_index, int phase_index, int n_control_volumes)
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
            void* ctx, void* phi_phase, void* phi_field,
            int tracer_index, int field_index,
            int phase_index_of_field, int n_control_volumes)
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
    given by ``tracer_index`. The output variable ``phi_presc`` is the prescribed mass fraction of the given tracer
    in respect to the mass of the mixture. Note that all boundary nodes will be populated with `phi_presc` value
    set by this `hook`.

    Please note that this `hook` sets the first mass fraction related boundary conditions value to
    the user defined tracer. However the hook :py:func:`HOOK_UPDATE_BOUNDARY_CONDITION_OF_MASS_FRACTION_OF_TRACER<alfasim_sdk.hook_specs.update_boundary_condition_of_mass_fraction_of_tracer>`
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
            void* ctx, void* phi_presc, int tracer_index)
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
            void* ctx, void* phi_presc, int tracer_index)
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

        int HOOK_CALCULATE_UCM_FRICTION_FACTOR_STRATIFIED(
            void* ctx, double* ff_wG, double* ff_wL, double* ff_i)
        {
            int errcode = -1;
            int G = TwoPhaseSystem::GAS
            int L = TwoPhaseSystem::LIQUID

            // Getting friction factor input data from context
            double alpha[2];
            errcode = alfasim_sdk_api.get_ucm_friction_factor_input_variable(
                ctx, &alpha[G], "alpha", TwoPhaseSystem::GAS);
            if (errcode != OK){ return errcode; }
            errcode = alfasim_plugins_api.get_ucm_friction_factor_input_variable(
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
        The same example presented in :py:func:`HOOK_CALCULATE_UCM_FRICTION_FACTOR_STRATIFIED<alfasim_sdk.hook_specs.calculate_ucm_friction_factor_stratified>`
        can be used, just change the `hook` name to `HOOK_CALCULATE_UCM_FRICTION_FACTOR_ANNULAR`.
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
        calculate_slip_velocity,
        calculate_slurry_viscosity,
        # Hooks related to Tracer added by plugin
        initialize_mass_fraction_of_tracer,
        calculate_mass_fraction_of_tracer_in_phase,
        calculate_mass_fraction_of_tracer_in_field,
        set_prescribed_boundary_condition_of_mass_fraction_of_tracer,
        update_boundary_condition_of_mass_fraction_of_tracer,
        # Hooks related to Unit Cell Model
        calculate_ucm_friction_factor_stratified,
        calculate_ucm_friction_factor_annular,
        # Extra Hooks (For testing)
        friction_factor,
        env_temperature,
        calculate_entrained_liquid_fraction,
        update_internal_deposition_layer,
    ],
)
