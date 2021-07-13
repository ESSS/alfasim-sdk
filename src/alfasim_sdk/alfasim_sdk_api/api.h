#ifndef _H_ALFASIM_SDK_API_PTRS
#define _H_ALFASIM_SDK_API_PTRS

#include <alfasim_sdk_api/common.h>

#if defined(_WIN32) && defined(_ALFASIM_EXPORT_SYMBOLS)
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT
#endif

/*! @file */

/*!
    Set the data provided from the plugin developer.

    When a plugin has internal data and it has to be accessed by all C/C++ `Hooks` during
    the simulation this function allows the plugin to ask the ALFAsim's solver to hold its
    internal data.

    @param[in] ctx ALFAsim's plugins context.
    @param[in] plugin_id Plugin ID.
    @param[in] data Plugin internal data.
    @param[in] thread_id Thread ID, see #get_thread_id for more information.
    @return An #error_code value.
*/
DLL_EXPORT int set_plugin_data(void* ctx, const char* plugin_id, void* data, int thread_id);

 /*!
    Gets the data provided from the plugin developer.

    Once the plugin set an internal data, it can be accessed from any C/C++ `Hook`
    during the simulation using this function.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Plugin internal data.
    @param[in] plugin_id Plugin ID.
    @param[in] thread_id Thread ID, see #get_thread_id for more information.
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_data(void* ctx, void** out, const char* plugin_id, int thread_id);

/*!
    Gives the number of running threads on the solver

    ALFAsim's Solver runs in multiple threads. To avoid data access concurrency
    problems the plugin developer must set one internal data to each running thread
    during the initialization. Then, with number of threads, the developer can do
    it properly.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] n_threads Number of threads.
    @return An #error_code value.
*/
DLL_EXPORT int get_number_of_threads(void* ctx, int* n_threads);

/*!
    Gives the current running thread id (in the solver process)

    Once the plugin sets one internal data to each running thread, to access this
    data properly it has to know which thread is trying to access this data. For
    that, this function retrieves this information from solver.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] thread_id Thread ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_thread_id(void* ctx, int* thread_id);

/*!
    Gets the data provided from the user on a Boolean input field.
    For more detail about the Boolean input field check `alfasim_sdk.types.Boolean`

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Retrieved variable value.
    @param[in] plugin_id Plugin ID.
    @param[in] var_name Name of the variable to be retrieved.
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_input_data_boolean(void* ctx, bool* out, const char* plugin_id, const char* var_name);

/*!
    Gets the data provided from the user on a Enum input field.
    For more detail about the Enum input field check `alfasim_sdk.types.Enum`.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Retrieved variable value.
    @param[in] plugin_id Plugin ID.
    @param[in] var_name Name of the variable to be retrieved.
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_input_data_enum(void* ctx, int* out, const char* plugin_id, const char* var_name);

/*!
    Gets the data provided from the user on a Quantity input field.
    For more detail about the quantity input field check `alfasim_sdk.types.Quantity`.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Retrieved variable value.
    @param[in] plugin_id Plugin ID.
    @param[in] var_name Name of the variable to be retrieved.
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_input_data_quantity(void* ctx, double* out, const char* plugin_id, const char* var_name);

/*!
    Gets the data provided from the user on a String input field.
    For more detail about the string input field check `alfasim_sdk.types.String`.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Retrieved variable value.
    @param[in] plugin_id Plugin ID.
    @param[in] var_name Name of the variable to be retrieved.
    @param[in] size Size of output string (param `out`).
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_input_data_string(void* ctx, char* out, const char* plugin_id, const char* var_name, int size);

/*!
    Gets the size of the data provided from the user on a String input field.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out String size of a variable in which its name is informed by `var_name`.
    @param[in] plugin_id Plugin ID.
    @param[in] var_name Name of the variable to be retrieved.
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_input_data_string_size(void* ctx, int* out, const char* plugin_id, const char* var_name);

/*!
    Gets the data provided from the user on a FileContent input field.
    For more detail about the FileContent input field check `alfasim_sdk.types.FileContent`

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Retrieved variable value.
    @param[in] plugin_id Plugin ID.
    @param[in] var_name Name of the variable to be retrieved.
    @param[in] size Size of output string (param `out`).
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_input_data_file_content(void* ctx, char* out, const char* plugin_id, const char* var_name, int size);

/*!
    Gets the size of the data provided from the user on a FileContent input field.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out File content size of a variable in which its name is informed by `var_name`.
    @param[in] plugin_id Plugin ID.
    @param[in] var_name Name of the variable to be retrieved.
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_input_data_file_content_size(void* ctx, int* out, const char* plugin_id, const char* var_name);

/*!
    Gets the values from a column of an input table. `column_id` is the string defined in the plugin's
    configuration file. If the `var_name` or the `column_id`  are invalid, #UNDEFINED_DATA is returned.

    Example of usage:
    ~~~~~{.cpp}
    int size = -1;
    double* values = NULL;
    int errcode = get_plugin_input_data_table_quantity(
        ctx,
        &values,
        &size,
        "temperature",
        get_plugin_id(),
        "Model.some_table"
    );
    for (int i = 0; i < size; ++i) {
        some_plugin_data = 1.1 * values[i];
    }
    ~~~~~

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Variable values array.
    @param[out] size Size of variable values array.
    @param[in] column_id Table column ID which values are retrieved.
    @param[in] plugin_id Plugin ID.
    @param[in] var_name Name of the variable to be retrieved.
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_input_data_table_quantity(
    void* ctx,
    double** out,
    int* size,
    const char* column_id,
    const char* plugin_id,
    const char* var_name
);

/*!
    Gets an ALFAsim input data internal Reference. Note that a Reference is a specific concept of
    ALFAsim-SDK and plugins - It is a way to retrieve data from an input outside of the current
    model. See the ALFAsim's SDK python configuration file for more information.

    Example of usage:
    ~~~~~{.cpp}
    void* tracer_ref = nullptr;
    errcode = get_plugin_input_data_reference(
        ctx, &tracer_ref, get_plugin_id(), "Model.tracer_reference");

    int tracer_id = -1;
    errcode = get_tracer_id(ctx, &tracer_id, tracer_ref);
    ~~~~~

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out ALFAsim data reference.
    @param[in] plugin_id Plugin ID.
    @param[in] var_name Name of the variable to be retrived.
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_input_data_reference(void* ctx, void** out, const char* plugin_id, const char* var_name);

/*!
    Get the number of selected references in a multiple-reference selection. User should be able to
    iterate over the selections to get information.

    Example of usage:
    ~~~~~{.cpp}
    int errcode = -1;
    int indexes_size = -1;
    errcode = get_plugin_input_data_multiplereference_selected_size(
        ctx, &indexes_size, get_plugin_id(), "Model.internal_multiple_reference");

    for (int i = 0; i < indexes_size; ++i) {
        auto value = -1.0;
        auto reference_str = std::string(
            "Model.internal_multiple_reference[" + std::to_string(i) + "]->quantity");

        errcode = get_plugin_input_data_quantity(
            ctx, &value, get_plugin_id(), reference_str.c_str());
        }
    }
    ~~~~~

    @param[in] ctx ALFAsim's plugins context.
    @param[out] indexes_size Number of selected references in a multiple reference input data.
    @param[in] plugin_id Plugin ID.
    @param[in] var_name Name of the variable.
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_input_data_multiplereference_selected_size(void* ctx, int* indexes_size, const char* plugin_id, const char* var_name);

/*!
    Gets the contents of a plugin-registered secondary variable (Given by name).

    It is allowed to the plugins to add new secondary variables via python config file. ALFAsim's
    solver registers/holds these variables and make them available in the solver `hooks` by this
    function.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Plugin-registered secondary variable values array.
    @param[in] variable_name Name of the secondary variable.
    @param[in] line_index It can represent Layer/Field/Phase ID, since the secondary variables can
                          be associated to different #MultiFieldDescriptionScope.
    @param[in] ts_scope A #TimestepScope value.
    @param[out] size Size of `out` array of values. It can be the number of volumes or number of faces
                     depending in which #GridScope the secondary variable was registered.
    @return An #error_code value.
*/
DLL_EXPORT int get_plugin_variable(void* ctx, void** out, const char* variable_name, int line_index, enum TimestepScope ts_scope, int* size);

/*!
    Gets the field ID of the given name. Although this depends on the hydrodynamic model being
    solved, common values include "gas", "oil", "droplet" and "bubble". This functions supports
    retrieve ID of field added by plugin.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Field ID.
    @param[in] name Name of the field to retrieve the ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_field_id(void* ctx, int* out, const char* name);

/*!
    Gets the phase ID of the given name. Although this depends on the hydrodynamic model
    being solved, common values include "gas", "oil" and "water". This functions supports
    retrieve ID of phase added by plugin.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Phase ID.
    @param[in] name Name of the phase to retrieve the ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_phase_id(void* ctx, int* out, const char* name);

/*!
    Gets the layer ID of the given name. Although this depends on the hydrodynamic model
    being solved, common values include "gas", "oil" and "water". This functions supports
    retrieve ID of layer added by plugin.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Layer ID.
    @param[in] name Name of the layer to retrieve the ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_layer_id(void* ctx, int* out, const char* name);

/*!
    Gives the number of fields in the hydrodynamic model being solved including dispersed
    and continuous fields. This information may be important when new fields are added by
    plugins.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Number of Fields.
    @return An #error_code value.
*/
DLL_EXPORT int get_number_of_fields(void* ctx, int* out);

/*!
    Gives the number of phases in the hydrodynamic model being solved. This information
    may be important when new phases are added by plugins.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Number of Phases.
    @return An #error_code value.
*/
DLL_EXPORT int get_number_of_phases(void* ctx, int* out);

/*!
    Gives the number of layers in the hydrodynamic model being solved. This information
    may be important when new layers are added by plugins.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Number of layers.
    @return An #error_code value.
*/
DLL_EXPORT int get_number_of_layers(void* ctx, int* out);

/*!
    Gives the number of phase pairs in the hydrodynamic model being solved. It depends
    on number of phases and may be important to calculate the phase pair state variables.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Number of phase pairs.
    @return An #error_code value.
*/
DLL_EXPORT int get_number_of_phase_pairs(void* ctx, int* out);

/*!
    Gets the primary field ID of the phase with given name. For example, the "oil" phase has
    primary field "oil". Different phases may have different primary fields. Use this function
    when you need a variable from a field, but you aren't sure about the field name, but you know
    the phase name.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Field ID.
    @param[in] name Name of the phase to retrieve the primary field ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_primary_field_id_of_phase(void* ctx, int* out, const char* name);

/*!
    Gets an array of phase IDs, in which each element is related to the fields in the hydrodynamic
    model. This function is usefull when is necessary to get information from a phase of a specific
    field (for example "oil in water" field is a "oil" phase).

    Example of usage:
    ~~~~~{.cpp}
    errcode = get_phase_id_of_fields(ctx, &phase_of_field, &size);
    int oil_in_water_phase_id = phase_of_field[oil_in_water_field_id];
    ~~~~~

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Phase IDs array.
    @param[out] size Size of the `out` array of IDs.
    @return An #error_code value.
*/
DLL_EXPORT int get_phase_id_of_fields(void* ctx, int** out, int* size);

/*!
    Gets an array of field IDs which are contained in a layer. For example: the "oil" layer could
    be formed by continuous "oil" field with dispersed "bubble"(gas) and dispersed "water in oil"
    fields (and also other dispersed fields added by plugins).

    Example of usage:
    ~~~~~{.cpp}
    errcode = get_field_ids_in_layer(ctx, &fields_in_Layer, layer_id, &size);
    ~~~~~

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Field IDs array.
    @param[in] layer_id Layer ID in which the field IDs are required.
    @param[out] size Size of the `out` array of IDs.
    @return An #error_code value.
*/
DLL_EXPORT int get_field_ids_in_layer(void* ctx, int** out, int layer_id, int* size);

/*!
    Gets the phase pair ID given a pair of phase ID's. It is important to calculate a phase pair
    properties (like surface tension) for more that one phase pair (For example: Gas-Oil,
    Gas-Water and Oil-Water).

    Since this function has phase ID's in parameters, it MUST be used in conjunction with
    #get_phase_id function.

    Example of usage:
    ~~~~~{.cpp}
    errcode = get_phase_id(ctx, &oil_phase_id, "oil");
    errcode = get_phase_id(ctx, &water_phase_id, "water");
    errcode = get_phase_pair_id(ctx, &oil_water_id, oil_phase_id, water_phase_id);
    ~~~~~

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Phase pair ID.
    @param[in] phase_0_id First phase ID of the pair.
    @param[in] phase_1_id Second phase ID of the pair.
    @return An #error_code value.
*/
DLL_EXPORT int get_phase_pair_id(void* ctx, int* out, int phase_0_id, int phase_1_id);

/*!
    Gets the current contents of a given state variable (For an array data pointer).
    A state variable is any variable calculated from pressure and temperature,
    as any thermodynamic variable.

    Example of usage:
    ~~~~~{.cpp}
    errcode = get_state_variable_array(
        ctx, &enthalpy, StateVariable::H, FIELD_GAS, &size);
    ~~~~~

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out State Variable values array.
    @param[in] state_var A #StateVariable value. It indicates which variable to be retrieved.
    @param[in] field_index Index of the field in which the state variable is retrieved.
    @param[out] size Size of the `out` array of values.
    @return An #error_code value.
*/
DLL_EXPORT int get_state_variable_array(
    void* ctx,
    double** out,
    enum StateVariable state_var,
    int field_index,
    int* size
);

/*!
    Gets the current contents of a given secondary variable (For an array data pointer).
    A secondary variable is any variable calculated in the solver iterative procedure.
    Note that not all variables are available at any time. If a given variable is not available
    in one of the chosen scopes, a #NOT_AVAILABLE_DATA error is returned.

    List of `variable_name` values:
    - `"rho"`: Density [kg/m3]
    - `"mu"`: Viscosity [Pa.s]
    - `"alpha"`: Volume Fraction [m3 of `field|layer|phase` /m3 of mixture]
    - `"mass_concentration"`: Mass Concentration [kg of `field|layer|phase` /m3 of mixture]
    - `"P"`: Pressure [Pa]
    - `"T"`: Temperature [K]
    - `"h"`: Specific Enthalpy [J/kg]
    - `"cp"`: Specific Heat Capacity [J/kg.K]
    - `"k"`: Thermal Conductivity [W/m.K]
    - `"eta_inner"`: Heat Transfer Coefficient between inner pipe wall and the fluid layers [W/m2.K]
    - `"U"`: Velocity [m/s]
    - `"U_superficial"`: Superficial Velocity [m/s]
    - `"RS"`: Gas mass fraction in gas/oil mixture [kg/kg]
    - `"RSW"`: Water vapour mass fraction in gas phase [kg/kg]
    - `"S_w"`: Wetted Perimeter of a layer [m]
    - `"ff_S_wall"`: Wall friction factor times wall perimeter [-]
    - `"ff_S_interface"`: Interface Friction factor times interface perimeter [-]
    - `"D"`: Pipe Inner Diameter [m]
    - `"A"`: Cross-sectional Area in each control volume [m2]
    - `"theta"`: Inclination of each control volume [rad]
    - `"dx"`: Control Volume Length along the Pipe Axis [m]
    - `"dv"`: Volume of the control volume [m3]
    - `"D_eff"`: Effective Pipe Inner Diameter, considering the internal deposit layers [m]
    - `"A_eff"`: Cross-sectional Area Effective in each control volume, considering the internal deposit layers [m2]
    - `"dv_eff"`: Effective Volume of the control volume, considering the internal deposit layers [m3]

    It is important to know that the listed `variable_name`s are no available in all #MultiFieldDescriptionScope
    and #GridScope. Because of that, the #error_code must be checked.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Variable values array.
    @param[in] variable_name String with the variable name. See the list of possible values above.
    @param[in] var_scope It must be configured to determine all scopes in which the variable will be
                         retrieved. See #VariableScope for more information.
    @param[in] line_index It can represent Layer/Field/Phase ID, since the secondary variables can
                          be associated to different #MultiFieldDescriptionScope. When it is a
                          #GLOBAL variable `line_index` must be 0.
    @param[out] size Size of the `out` array of values.
    @return An #error_code value.
*/
DLL_EXPORT int get_simulation_array(
    void* ctx,
    double** out,
    const char* variable_name,
    struct VariableScope var_scope,
    int line_index,
    int* size
);

/*!
    Gets the current contents of a given tracer mass fraction (For an array data pointer).
    A tracer mass fraction is calculated in the extra solver iterative procedure.
    Note that not all tracer mass fraction are available at any time.
    If a given tracer mass fraction (in an inexistent field) is not available,
    a #NOT_AVAILABLE_DATA error is returned.

    List of `variable_name_c` values:
    - `"phi"`: Mass Fraction [kg of tracer (in `field|phase`) / kg of mixture]

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Variable values array.
    @param[in] variable_name_c String with the variable name. See the list of possible values above.
    @param[in] var_scope It must be configured to determine all scopes in which the variable will be
                         retrieved. See #VariableScope for more information.
    @param[in] tracer_index Tracer ID, it can be retrieved by #get_tracer_id.
    @param[in] line_index It can represent Field or Phase ID, since the tracer masss fraction can
                          be calculated related to Field or Phase. When it is the mass fraction on
                          mixture the `line_index` must be 0.
    @param[out] size Size of the `out` array of values.
    @return An #error_code value.
*/
DLL_EXPORT int get_simulation_tracer_array(
    void* ctx,
    double** out,
    const char* variable_name_c,
    struct VariableScope var_scope,
    int tracer_index,
    int line_index,
    int* size
);

/*!
    Gets the current contents of a given secondary variable (For a single quantity).
    A secondary variable is any variable calculated in the solver iterative procedure.
    Note that not all variables are available at any time. If a given variable is not available,
    a #NOT_AVAILABLE_DATA error is returned.

     List of `variable_name_c` values:
    - `"dt"`: Time Step [s]
    - `"time"`: Current time [s]

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Variable value.
    @param[in] ts_scope #TimestepScope value.
    @param[in] variable_name_c String with the variable name. See the list of possible values above.
    @return An #error_code value.

    It is important to know that `dt` may have value equal to `NAN` (Not a number) during the steady
    state simulation. In this case the plugin must handle it and not use this value.
*/
DLL_EXPORT int get_simulation_quantity(
    void* ctx,
    double* out,
    enum TimestepScope ts_scope,
    const char* variable_name_c
);

/*!
    Gets the flow pattern for each control volume.

    List of possible values of `Flow Pattern` is:
    - `0 - Unknown`
    - `1 - Stratified`
    - `2 - Dispersed Bubble`
    - `3 - Bubble`
    - `4 - Slug`
    - `5 - Annular Mist`

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Flow Pattern values array. See list of possible values above.
    @param[in] grid_scope A #GridScope value.
    @param[in] ts_scope A #TimestepScope value.
    @param[in] size Size of out array of values.
    @return An #error_code value.
*/
DLL_EXPORT int get_flow_pattern(
    void* ctx,
    int** out,
    enum GridScope grid_scope,
    enum TimestepScope ts_scope,
    int* size
);

/*!
    Gets the liquid-liquid flow pattern for each control volume. Related to the UCM
    liquid-liquid system.

    List of possible values of `Liquid-Liquid Flow Pattern` is:
    - `0 - Unknown`: Unknown Flow Pattern.
    - `1 - Ambivalent`: Ambivalent Flow Pattern between Dispersed Oil and Dispersed Water.
    - `2 - Dispersed Oil`: Dispersed oil in continuous water.
    - `3 - Dispersed Water`: Dispersed water in continuous Oil.
    - `4 - Separated`: Separated continuous oil and continuous water.
    - `5 - Separated Mixed`: Separated with dispersed oil and water droplets.
    - `6 - Separated Wavy`: Separated with waves.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Liquid-Liquid Flow Pattern values array. See list of possible values above.
    @param[in] grid_scope A #GridScope value.
    @param[in] ts_scope A #TimestepScope value.
    @param[in] size Size of out array of values.
    @return An #error_code value.
*/
DLL_EXPORT int get_liqliq_flow_pattern(
    void* ctx,
    int** out,
    enum GridScope grid_scope,
    enum TimestepScope ts_scope,
    int* size
);

/*!
    Retrieves the tracer ID given a tracer reference. A tracer reference may be obtained from the
    user input data (See #get_plugin_input_data_reference API function for an example).

    @param[in] ctx ALFAsim's plugins context.
    @param[out] tracer_id Tracer ID.
    @param[in] reference Tracer reference.
    @return An #error_code value.
*/
DLL_EXPORT int get_tracer_id(void* ctx, int* tracer_id, void* reference);

/*!
    Retrieves the size of the tracer name, given a tracer reference. A tracer reference may be
    obtained from the user input data (See #get_plugin_input_data_reference API function for an
    example).

    @param[in] ctx ALFAsim's plugins context.
    @param[out] tracer_name_size Size of tracer name string.
    @param[in] reference Tracer reference.
    @return An #error_code value.
*/
DLL_EXPORT int get_tracer_name_size(void* ctx, int* tracer_name_size, void* reference);

/*!
    Retrieves the tracer name, given a tracer reference. The `tracer_name` parameter must be a valid
    and pre-allocated memory region where the name string will be copied to. A tracer reference may
    be obtained from the user input data (See #get_plugin_input_data_reference API function for an
    example).

    Example of usage:
    ~~~~~{.cpp}
    int tracer_name_size = -1;
    errcode = get_tracer_name_size(ctx, &tracer_name_size, tracer_ref);

    char* tracer_name = (char*)malloc(sizeof(char) * tracer_name_size);
    errcode = get_tracer_name(
        ctx, tracer_name, tracer_ref, tracer_name_size);
    std::cout << "TRACER NAME: " << tracer_name << std::endl;
    free(tracer_name);
    ~~~~~

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out String with tracer name.
    @param[in] reference Tracer reference.
    @param[in] size Size of `out` string.
    @return An #error_code value.
*/
DLL_EXPORT int get_tracer_name(void* ctx, char* out, void* reference, int size);

/*!
    Gets the tracer reference for a given tracer name. This function is important to obtain the
    tracer reference of a user defined tracer added by the plugin.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] reference Tracer reference.
    @param[in] tracer_name Tracer name.
    @param[in] plugin_id Plugin ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_tracer_ref_by_name(void* ctx, void** reference, const char* tracer_name, const char* plugin_id);

/*!
    Gets the partition coefficient input data for a given tracer reference. The `phase_id` must also
    be given (See #get_phase_id API function). A tracer reference may be obtained from the user
    input data (See #get_plugin_input_data_reference API function for an example).

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Partition coefficient value related to the specified phase.
    @param[in] reference Tracer reference.
    @param[in] phase_id Phase ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_tracer_partition_coefficient(void* ctx, double* out, void* reference, int phase_id);

/*!
    Gets the wall interface temperature for a given control volume. Each control volume has an array
    of temperatures, one for each wall layer. The temperatures are given in the wall interfaces.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Wall interfaces temperature values array.
    @param[in] control_volume Control Volume ID.
    @param[in] ts_scope #TimestepScope value.
    @param[in] size Size of `out` array of values.
    @return An #error_code value.
*/
DLL_EXPORT int get_wall_interfaces_temperature(
    void* ctx,
    double** out,
    int control_volume,
    enum TimestepScope ts_scope,
    int* size
);

/*!
    Gets the current UCM (unit cell model) input data for friction factor calculation.
    Any available variable by this function is considered for a unit cell, which means
    that there are variables with one value and there are variables with two values
    related to the two phase system (GAS and LIQUID).
    If a given variable name is not available, a #NOT_AVAILABLE_DATA error is returned.

    List of `variable_name` with two values (Two phase):
    - `"alpha"`: Volume Fraction [m3 of `phase` /m3 of mixture]
    - `"rho"`: Density [kg/m3]
    - `"mu"`: Viscosity [Pa.s]
    - `"U"`: Velocity [m/s]

    It is important to know that the listed `variable_name`s are not available in any phase, only for
    two phase systems, in which `GAS` (0, zero) and `LIQUID` (1, One)(sum of all liquid phases) are
    the possible values, and they are available in the #TwoPhaseSystem enumeration.
    Because of that, the #error_code must be checked.

    List of `variable_name` with one value:
    - `"D"`: Unit Cell Inner Diameter [m]
    - `"ks"`: Roughness [m]
    - `"theta"`: Inclination of the Unit Cell [rad]
    - `"sigma"`: Gas-liquid Surface Tension [N/m]

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Variable value.
    @param[in] var_name String with the variable name. See the list of possible values above.
    @param[in] phase_id A #TwoPhaseSystem value. When the requested variable is not associated
                            to a phase any value can be passed.
    @return An #error_code value.
*/
DLL_EXPORT int get_ucm_friction_factor_input_variable(
    void* ctx, double* out, const char* var_name, int phase_id
);

/*!
    Gets the current UCM (unit cell model) fluid geometrical properties for friction
    factor calculation.

    During the implementation of any HOOK related to the UCM friction factor, this
    function provides the following fluid geometrical properties:
    - `"S_w"`: Wetted perimeters of phases [m].
    - `"S_i"`: Interface perimeter [m].
    - `"H"`: Phase height [m].

    @param[in] ctx ALFAsim's plugins context.
    @param[out] S_w Wetted Perimeters [m].
    @param[out] S_i Interface Perimeter [m].
    @param[out] H   Phase height [m]. For annular flow, H[GAS] is the core diameter and H[LIQUID] is
                     the total liquid film height.
    @param[in] alpha_G  Unit Cell Gas Volume Fraction [m3 of `gas phase` /m3 of mixture].
    @param[in] D        Unit Cell Inner Diameter [m].
    @return An #error_code value.

    It is important to know that `S_w` and `H` must be pointers to an array of size two (GAS and LIQUID).
*/
DLL_EXPORT int get_ucm_fluid_geometrical_properties(
    void* ctx,
    double* S_w,
    double* S_i,
    double* H,
    double alpha_G,
    double D
);

/*!
    Gets the current control volume input data for liquid-liquid flow Pattern calculation.
    Any available variable by this function is considered for a control volume, which
    means that there are variables with one value and there are variables with two values
    related to the liquid-liquid system (OIL and WATER).
    If a given variable name is not available, a #NOT_AVAILABLE_DATA error is returned.

    List of `variable_name` with two values (Oil and Water):
    - `"rho"`: Density [kg/m3]
    - `"mu"`: Viscosity [Pa.s]
    - `"U_S"`: Superficial Velocity [m/s]

    It is important to know that the listed `variable_name`s are not available in any phase, only for
    liquid-liquid systems, in which `OIL` (0, zero) and `WATER` (1, One) are the possible values, and
    they are available in the #LiquidLiquidSystem enumeration.
    Because of that, the #error_code must be checked.

    List of `variable_name` with one value:
    - `"D_h"`: Unit Cell Liquid (Oil-Water) Hydraulic Diameter [m]
    - `"ks"`: Absolute Roughness [m]
    - `"theta"`: Inclination of the Unit Cell [rad]
    - `"sigma"`: Liquid-liquid (Oil-Water) Surface Tension [N/m]

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Variable value.
    @param[in] var_name String with the variable name. See the list of possible values above.
    @param[in] phase_id A #LiquidLiquidSystem value. When the requested variable is not associated
                            to a phase any value can be passed.
    @return An #error_code value.
*/
DLL_EXPORT int get_liq_liq_flow_pattern_input_variable(
    void* ctx, double* out, const char* var_name, int phase_id
);

/*!
    Gets the current input data for liquid effective viscosity calculation. Any available variable by
    this function is considered for a control volume, which means that there are variables with one
    value and there are variables with two values related to the liquid-liquid system (OIL and WATER).
    If a given variable name is not available, a #NOT_AVAILABLE_DATA error is returned.

    List of `variable_name` with two values (Oil and Water):
    - `"rho"`: Density [kg/m3]
    - `"mu"`: Viscosity [Pa.s]
    - `"U_S"`: Superficial Velocity [m/s]

    It is important to know that the listed `variable_name`s are not available in any phase, only for
    liquid-liquid systems, in which `OIL` (0, zero) and `WATER` (1, One) are the possible values, and
    they are available in the #LiquidLiquidSystem enumeration.
    Because of that, the #error_code must be checked.

    List of `variable_name` with one value:
    - `"alpha_w"` : Water Volume Fraction [m3 of `water phase` / m3 of `liquid(Oil+Water) phase`]
    - `"D_h"`: Unit Cell Liquid (Oil-Water) Hydraulic Diameter [m]
    - `"ks"`: Absolute Roughness [m]
    - `"theta"`: Inclination of the Unit Cell [rad]
    - `"sigma"`: Liquid-liquid (Oil-Water) Surface Tension [N/m]

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Variable value.
    @param[in] var_name String with the variable name. See the list of possible values above.
    @param[in] phase_id A #LiquidLiquidSystem value. When the requested variable is not associated
                            to a phase any value can be passed.
    @return An #error_code value.
*/
DLL_EXPORT int get_liquid_effective_viscosity_input_variable(
    void* ctx, double* out, const char* var_name, int phase_id
);

/*!
    Gets the current input data for Gas-Liquid surface tension calculation. Any available variable by
    this function is considered for a control volume, which means that there are variables with one
    value and there are variables with two values related to the liquid-liquid system (OIL and WATER).
    If a given variable name is not available, a #NOT_AVAILABLE_DATA error is returned.

    List of `variable_name` with two values (Oil and Water):
    - `"sigma_gll"`: Gas-Liquid-Liquid (Gas-Oil or Gas-Water) Surface Tension [N/m]

    It is important to know that the listed `variable_name`s are not available in any phase, only for
    liquid-liquid systems, in which `OIL` (0, zero) and `WATER` (1, One) are the possible values, and
    they are available in the #LiquidLiquidSystem enumeration.
    Because of that, the #error_code must be checked.

    List of `variable_name` with one value:
    - `"alpha_w"` : Water Volume Fraction [m3 of `water phase` / m3 of `liquid(Oil+Water) phase`]

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Variable value.
    @param[in] var_name String with the variable name. See the list of possible values above.
    @param[in] phase_id A #LiquidLiquidSystem value. When the requested variable is not associated
                            to a phase any value can be passed.
    @return An #error_code value.
*/
DLL_EXPORT int get_gas_liq_surface_tension_input_variable(
    void* ctx, double* out, const char* var_name, int phase_id
);

/*!
    Gets the current input data for Shear force calculation. Any available variable by this function
    is considered for a control volume, which means that there are variables with one value and there
    are variables with two values related to the liquid-liquid system (OIL and WATER).
    If a given variable name is not available, a #NOT_AVAILABLE_DATA error is returned.

    The variables available are the same as #get_liq_liq_flow_pattern_input_variable and
    its documentation should be visited for more details.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Variable value.
    @param[in] var_name String with the variable name. See the list of possible values above.
    @param[in] phase_id A #LiquidLiquidSystem value. When the requested variable is not associated
                            to a phase any value can be passed.
    @return An #error_code value.
*/
DLL_EXPORT int get_liq_liq_shear_force_per_volume_input_variable(
    void* ctx, double* out, const char* var_name, int phase_id
);

/*!
    Gets the relative emulsion viscosity for liquid-liquid calculations.

    During the implementation of any HOOK related to the Liquid-Liquid Mechanistic model, this
    function provides the relative emulsion viscosity from Emulsion Model (selected through GUI).

    It allows the plugin HOOKs to use the same emulsion model used internally by ALFAsim.

    The definition of relative viscosity is given by the ratio between the apparent viscosity
    (dispersed field + continuous field) and the continuous field.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Relative Emulsion Viscosity [-].
    @param[in] mu_disp Dispersed Field Viscosity [Pa.s].
    @param[in] mu_cont Continuous Field Viscosity [Pa.s].
    @param[in] alpha_disp_in_layer Dispersed Field Volume Fraction in the layer (emulsion) [m3 of dispersed field /m3 of layer].
    @param[in] disp_field_id  Dispersed Field Id (Can be "oil in water" or "water in oil" fields).
    @param[in] cont_field_id  Continuous Field Id (Can be "oil" or "water" fields).
    @return An #error_code value.

    It is important to know that `disp_field_id` and `cont_field_id` must be passed because
    the emulsion model can have different correlations for each one.
    To use the correct Field Ids the API function #get_field_id must be used.
*/
DLL_EXPORT int get_relative_emulsion_viscosity(
    void* ctx,
    double* out,
    double mu_disp,
    double mu_cont,
    double alpha_disp_in_layer,
    int disp_field_id,
    int cont_field_id
);

#endif
