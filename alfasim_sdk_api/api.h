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
    that, this function retrieves this information from Solver.

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
        plugin_id,
        "some_table"
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
        ctx, &tracer_ref, plugin_id, "Model.tracer_reference");

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
        ctx, &indexes_size, plugin_id, "Model.internal_multiple_reference");

    for (int i = 0; i < indexes_size; ++i) {
        auto value = -1.0;
        auto reference_str = std::string(
            "Model.internal_multiple_reference[" + std::to_string(i) + "]->quantity");

        errcode = get_plugin_input_data_quantity(
            ctx, &value, plugin_id, reference_str.c_str());
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
    Gets the field ID of the given name. Althought this depends on the hydrodynamic model being
    solved, common values include "gas", "liquid", "droplet" and "bubble". This functions supports
    retrieve ID of field added by plugin.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Field ID.
    @param[in] name Name of the field to retrieve the ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_field_id(void* ctx, int* out, const char* name);

/*!
    Gets the primary field ID of the phase with given name. For example, the "liquid" phase has
    primary field "liquid". Different phases may have different primary fields. Use this function
    when you need a variable from a field, but you aren't sure about the field name, but you know
    the phase name.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Field ID.
    @param[in] name Name of the phase to retrieve the primary field ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_primary_field_id_of_phase(void* ctx, int* out, const char* name);

/*!
    Gets the phase ID of the given name. Althought this depends on the hydrodynamic model
    being solved, common values include "gas", "liquid" and "water". This functions supports
    retrieve ID of phase added by plugin.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Phase ID.
    @param[in] name Name of the phase to retrieve the ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_phase_id(void* ctx, int* out, const char* name);

/*!
    Gets the layer ID of the given name. Althought this depends on the hydrodynamic model
    being solved, common values include "gas", "liquid" and "water". This functions supports
    retrieve ID of layer added by plugin.

    @param[in] ctx ALFAsim's plugins context.
    @param[out] out Layer ID.
    @param[in] name Name of the layer to retrieve the ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_layer_id(void* ctx, int* out, const char* name);

/*!
    Gets the current contents of a given state variable (For an array data pointer).
    A state variable is any variable calculated from pressure and temperature,
    as any thermodynamic variable.

    Example of usage:
    ~~~~~{.cpp}
    errcode = get_state_variable_array(
        ctx, enthalpy, StateVariable::H, FIELD_GAS, size);
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
    Note that not all variables are available at any time. If a given variable is not available,
    a #NOT_AVAILABLE_DATA error is returned.

    List of `variable_name` values:
    - `"rho"`: Density [kg/m3]
    - `"mu"`: Viscosity [Pa.s]
    - `"alpha"`: Volume Fraction [m3 of `field|layer|phase` /m3 of mixture]
    - `"mass_concentration"`: Mass Concentration [kg of `field|layer|phase` /m3 of mixture]
    - `"P"`: Pressure [Pa]
    - `"T"`: Temperature [K]
    - `"cp"`: Specific Heat Capacity [J/kg.K]
    - `"k"`: Thermal Conductivity [W/m.K]
    - `"U"`: Velocity [m/s]
    - `"D"`: Pipe Inner Diameter [m]
    - `"dx"`: Control Volume Length along the Pipe Axis [m]
    - `"dv"`: Volume of the Control volume [m]

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
    char* variable_name,
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
    char* variable_name_c,
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
*/
DLL_EXPORT int get_simulation_quantity(
    void* ctx,
    double* out,
    enum TimestepScope ts_scope,
    char* variable_name_c
);

/*!
    Gets the flow pattern for each control volume.

    List of possible values of `Flow Pattern` is:
    - `0 - Unknown`
    - `1 - Dispersed Bubble`
    - `2 - Froth`
    - `3 - Stratified Smooth`
    - `4 - Stratified Wavy`
    - `5 - Annular Mist`
    - `6 - Bubble`
    - `7 - Slug`

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
    Gets the wall layer ID in the given control volume, with a given material name.

    @param[in] ctx ALFAsim's plugins context.
    @param[in] control_volume Control Volume ID.
    @param[in] material_name Material name.
    @param[out] out Wall Layer ID.
    @return An #error_code value.
*/
DLL_EXPORT int get_wall_layer_id(void* ctx, int control_volume, const char* material_name, int* out);

/*!
    Set a property in the given wall layer ID (Use #get_wall_layer_id to obtain it), in a given
    control volume. Please note that the new value is assumed to be physical, as no sanity check is
    performed by the solver.

    @param[in] ctx ALFAsim's plugins context.
    @param[in] control_volume Control Volume ID.
    @param[in] wall_layer_id Wall Layer ID.
    @param[in] property_id A #WallLayerProperty value.
    @param[in] new_value A new value to be set in the specified property.
    @return An #error_code value.
*/
DLL_EXPORT int set_wall_layer_property(void* ctx, int control_volume, int wall_layer_id, enum WallLayerProperty property_id, double new_value);

#endif
