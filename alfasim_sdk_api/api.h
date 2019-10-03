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

    @param[in] ctx ALFAsim's plugins context
    @param[in] plugin_id Plugin ID
    @param[in] data Plugin internal data
    @param[in] thread_id Thread ID, see #get_thread_id for more information
    @return An #error_code value
*/
DLL_EXPORT int set_plugin_data(void* ctx, const char* plugin_id, void* data, int thread_id);

 /*!
    Gets the data provided from the plugin developer.

    Once the plugin set an internal data, it can be accessed from any C/C++ `Hook`
    during the simulation using this function.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Plugin internal data
    @param[in] plugin_id Plugin ID
    @param[in] thread_id Thread ID, see #get_thread_id for more information
    @return An #error_code value
*/
DLL_EXPORT int get_plugin_data(void* ctx, void** out, const char* plugin_id, int thread_id);

/*!
    Gives the number of running threads on the solver

    ALFAsim's Solver runs in multiple threads. To avoid data access concurrency
    problems the plugin developer must set one internal data to each running thread
    during the initialization. Then, with number of threads, the developer can do
    it properly.

    @param[in] ctx ALFAsim's plugins context
    @param[out] n_threads Number of threads
    @return An #error_code value
*/
DLL_EXPORT int get_number_of_threads(void* ctx, int* n_threads);

/*!
    Gives the current running thread id (in the solver process)

    Once the plugin sets one internal data to each running thread, to access this
    data properly it has to know which thread is trying to access this data. For
    that, this function retrieves this information from Solver.

    @param[in] ctx ALFAsim's plugins context
    @param[out] thread_id Thread ID
    @return An #error_code value
*/
DLL_EXPORT int get_thread_id(void* ctx, int* thread_id);

/*!
    Gets the data provided from the user on a Boolean input field.
    For more detail about the Boolean input field check `alfasim_sdk.types.Boolean`

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Retrieved variable value
    @param[in] plugin_id Plugin ID
    @param[in] var_name Name of the variable to be retrieved
    @return An #error_code value
*/
DLL_EXPORT int get_plugin_input_data_boolean(void* ctx, bool* out, const char* plugin_id, const char* var_name);

/*!
    Gets the data provided from the user on a Enum input field.
    For more detail about the Enum input field check `alfasim_sdk.types.Enum`.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Retrieved variable value
    @param[in] plugin_id Plugin ID
    @param[in] var_name Name of the variable to be retrieved
    @return An #error_code value
*/
DLL_EXPORT int get_plugin_input_data_enum(void* ctx, int* out, const char* plugin_id, const char* var_name);

/*!
    Gets the data provided from the user on a Quantity input field.
    For more detail about the quantity input field check `alfasim_sdk.types.Quantity`.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Retrieved variable value
    @param[in] plugin_id Plugin ID
    @param[in] var_name Name of the variable to be retrieved
    @return An #error_code value
*/
DLL_EXPORT int get_plugin_input_data_quantity(void* ctx, double* out, const char* plugin_id, const char* var_name);

/*!
    Gets the data provided from the user on a String input field.
    For more detail about the string input field check `alfasim_sdk.types.String`.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Retrieved variable value
    @param[in] plugin_id Plugin ID
    @param[in] var_name Name of the variable to be retrieved
    @param[in] size Size of output string (param `out`)
    @return An #error_code value
*/
DLL_EXPORT int get_plugin_input_data_string(void* ctx, char* out, const char* plugin_id, const char* var_name, int size);

/*!
    Gets the size of the data provided from the user on a String input field.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out String size of a variable in which its name is informed by `var_name`
    @param[in] plugin_id Plugin ID
    @param[in] var_name Name of the variable to be retrieved
    @return An #error_code value
*/
DLL_EXPORT int get_plugin_input_data_string_size(void* ctx, int* out, const char* plugin_id, const char* var_name);

/*!
    Gets the data provided from the user on a FileContent input field.
    For more detail about the FileContent input field check `alfasim_sdk.types.FileContent`

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Retrieved variable value
    @param[in] plugin_id Plugin ID
    @param[in] var_name Name of the variable to be retrieved
    @param[in] size Size of output string (param `out`)
    @return An #error_code value
*/
DLL_EXPORT int get_plugin_input_data_file_content(void* ctx, char* out, const char* plugin_id, const char* var_name, int size);

/*!
    Gets the size of the data provided from the user on a FileContent input field.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out File content size of a variable in which its name is informed by `var_name`
    @param[in] plugin_id Plugin ID
    @param[in] var_name Name of the variable to be retrieved
    @return An #error_code value
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

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Variable values array
    @param[out] size Size of variable values array
    @param[in] column_id Table column ID which values are retrieved
    @param[in] plugin_id Plugin ID
    @param[in] var_name Name of the variable to be retrieved
    @return An #error_code value
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

    @param[in] ctx ALFAsim's plugins context
    @param[out] out ALFAsim data reference
    @param[in] plugin_id Plugin ID
    @param[in] var_name Name of the variable to be retrived
    @return An #error_code value
*/
DLL_EXPORT int get_plugin_input_data_reference(void* ctx, void** out, const char* plugin_id, const char* var_name);

/*!
    Gets the contents of a plugin-registered secondary variable (Given by name).

    It is allowed to the plugins to add new secondary variables via python config file. ALFAsim's
    solver registers/holds these variables and make them available in the solver `hooks` by this
    function.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Plugin-registered secondary variable values array
    @param[in] variable_name Name of the secondary variable
    @param[in] line_index It can represent Layer/Field/Phase ID, since the secondary variables can
                          be associated to different #MultiFieldDescriptionScope
    @param[in] ts_scope A #TimestepScope value
    @param[out] size Size of `out` array of values. It can be the number of volumes or number of faces
                     depending in which #GridScope the secondary variable was registered.
    @return An #error_code value
*/
DLL_EXPORT int get_plugin_variable(void* ctx, void** out, const char* variable_name, int line_index, enum TimestepScope ts_scope, int* size);

/*!
    Gets the field ID of the given name. Althought this depends on the hydrodynamic model being
    solved, common values include "gas", "liquid", "droplet" and "bubble". This functions supports
    retrieve ID of field added by plugin.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Field ID
    @param[in] name Name of the field to retrieve the ID
    @return An #error_code value
*/
DLL_EXPORT int get_field_id(void* ctx, int* out, const char* name);

/*!
    Gets the primary field ID of the phase with given name. For example, the "liquid" phase has
    primary field "liquid". Different phases may have different primary fields. Use this function
    when you need a variable from a field, but you aren't sure about the field name, but you know
    the phase name.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Field ID
    @param[in] name Name of the phase to retrieve the primary field ID
    @return An #error_code value
*/
DLL_EXPORT int get_primary_field_id_of_phase(void* ctx, int* out, const char* name);

/*!
    Gets the phase ID of the given name. Althought this depends on the hydrodynamic model
    being solved, common values include "gas", "liquid" and "water". This functions supports
    retrieve ID of phase added by plugin.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Phase ID
    @param[in] name Name of the phase to retrieve the ID
    @return An #error_code value
*/
DLL_EXPORT int get_phase_id(void* ctx, int* out, const char* name);

/*!
    Gets the layer ID of the given name. Althought this depends on the hydrodynamic model
    being solved, common values include "gas", "liquid" and "water". This functions supports
    retrieve ID of layer added by plugin.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Layer ID
    @param[in] name Name of the layer to retrieve the ID
    @return An #error_code value
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

    @param[in] ctx ALFAsim's plugins context
    @param[out] out State Variable values array
    @param[in] state_var A #StateVariable value. It indicates which variable to be retrieved.
    @param[in] field_index Index of the field in which the state variable is retrieved.
    @param[Out] size Size of the `out` array of values
    @return An #error_code value
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
    a NOT_AVAILABLE_DATA error is returned.

    @param[in] ctx ALFAsim's plugins context
    @param[out] out Variable values array
    @param[in] variable_name Variable name. **MUST BE LISTED**
    @param[in] var_scope It must be configured to determine all scopes in which the variable will be
                         retrieved. See #VariableScope for more information.
    @param[in] line_index It can represent Layer/Field/Phase ID, since the secondary variables can
                          be associated to different #MultiFieldDescriptionScope
    @param[Out] size Size of the `out` array of values
    @return An #error_code value
*/
DLL_EXPORT int get_simulation_array(
    void* ctx,
    double** out,
    char* variable_name,
    struct VariableScope var_scope,
    int line_index,
    int* size
);

DLL_EXPORT int get_simulation_tracer_array(
    void* ctx,
    double** out,
    char* variable_name_c,
    struct VariableScope var_scope,
    int tracer_index,
    int line_index,
    int* size
);
DLL_EXPORT int get_simulation_quantity(
    void* ctx,
    double* out,
    enum TimestepScope ts_scope,
    char* variable_name_c
);
DLL_EXPORT int get_wall_interfaces_temperature(
    void* ctx,
    double** out,
    int control_volume,
    enum TimestepScope ts_scope,
    int* size
);
DLL_EXPORT int get_flow_pattern(
    void* ctx,
    int** out,
    enum GridScope grid_scope,
    enum TimestepScope ts_scope,
    int* size
);


DLL_EXPORT int get_tracer_id(void* ctx, int* tracer_id, void* reference);
DLL_EXPORT int get_tracer_name_size(void* ctx, int* tracer_name_size, void* reference);
DLL_EXPORT int get_tracer_name(void* ctx, char* out, void* reference, int size);
DLL_EXPORT int get_tracer_ref_by_name(void* ctx, void** reference, const char* tracer_name, const char* plugin_id);
DLL_EXPORT int get_tracer_partition_coefficient(void* ctx, double* out, void* reference, int phase_id);

DLL_EXPORT int get_wall_layer_id(void* ctx, int control_volume, const char* material_name, int* out);
DLL_EXPORT int set_wall_layer_property(void* ctx, int control_volume, int wall_layer_id, enum WallLayerProperty property_id, double new_value);

DLL_EXPORT int get_plugin_input_data_multiplereference_selected_size(void* ctx, int* indexes_size, const char* plugin_id, const char* var_name);

#endif
