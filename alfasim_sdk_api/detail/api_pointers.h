#ifndef _H_ALFASIM_SDK_API
#define _H_ALFASIM_SDK_API

typedef int (*set_plugin_data_func)(void*, const char*, void*);
set_plugin_data_func set_plugin_data;


/**
*   get_plugin_input_data
*
*   This function is used to get the data provided from the user
*/
typedef int (*get_plugin_data_func)(void*, void**, const char*);
get_plugin_data_func get_plugin_data;


/**
*   get_plugin_input_data_boolean
*
*   Get the data provided from the user on a Boolean input field.
*       For more detail about the Boolean input field check alfasim_sdk.types.Boolean
*/
typedef int (*get_plugin_input_data_boolean_func)(void*, bool*, const char*, const char*);
get_plugin_input_data_boolean_func get_plugin_input_data_boolean;


/**
*   get_plugin_input_data_enum
*
*   Get the data provided from the user on a Enum input field.
*       For more detail about the Enum input field check alfasim_sdk.types.Enum
*/
typedef int (*get_plugin_input_data_enum_func)(void*, int*, const char*, const char*);
get_plugin_input_data_enum_func get_plugin_input_data_enum;

/**
*   get_plugin_input_data_quantity
*
*   Get the data provided from the user on a Quantity input field.
*       For more detail about the quantity input field check alfasim_sdk.types.Quantity
*/
typedef int (*get_plugin_input_data_quantity_func)(void*, double*, const char*, const char*);
get_plugin_input_data_quantity_func get_plugin_input_data_quantity;

/**
*   get_plugin_input_data_string
*
*   Get the data provided from the user on a String input field.
*       For more detail about the string input field check alfasim_sdk.types.String
*/
typedef int (*get_plugin_input_data_string_func)(void*, char*, const char*, const char*, int);
get_plugin_input_data_string_func get_plugin_input_data_string;

/**
*   get_plugin_input_data_string_size
*
*   Get the size of the data provided from the user on a String input field.
**/
typedef int (*get_plugin_input_data_string_size_func)(void*, int*, const char*, const char*);
get_plugin_input_data_string_size_func get_plugin_input_data_string_size;

/**
*   get_plugin_variable
*
*   Gets the contents of a plugin-defined variable (Given by name)
**/
typedef int (*get_plugin_variable_func)(void* ctx, void** out, const char* variable_name, int line_index, int timestep, int* size);
get_plugin_variable_func get_plugin_variable;

/**
*   get_field_id
*
*   Gets the field ID of the given name. Althought this depends on the hydrodynamic model
*   being solved, common values include "gas", "liquid", "droplet" and "bubble".
**/
typedef int (*get_field_id_func)(void* ctx, int* out, const char* name);
get_field_id_func get_field_id;

/**
*   get_primary_field_of_phase
*
*   Gets the primary field ID of the phase with given name. For example, the "liquid" phase has
*   primary field "liquid". Different phases may have different primary fields. Use this function
*   when you need a variable from a field, but you aren't sure about the field name, but you know
*   the phase name.
**/
typedef int (*get_primary_field_id_of_phase_func)(void* ctx, int* out, const char* name);
get_primary_field_id_of_phase_func get_primary_field_id_of_phase;

/**
*   get_phase_id
*
*   Gets the phase ID of the given name. Althought this depends on the hydrodynamic model
*   being solved, common values include "gas", "liquid" and "water"
**/
typedef int (*get_phase_id_func)(void* ctx, int* out, const char* name);
get_phase_id_func get_phase_id;

/**
*   get_layer_id
*
*   Gets the layer ID of the given name. Althought this depends on the hydrodynamic model
*   being solved, common values include "gas", "liquid" and "water"
**/
typedef int (*get_layer_id_func)(void* ctx, int* out, const char* name);
get_layer_id_func get_layer_id;

/**
*   get_simulation_array
*
*   Get the current contents of a given secondary variable (For an array data pointer).
*   A secondary variable is any variable calculated in the solver iterative procedure.
*   Note that not all variables are available at any time. If a given variable is not available,
*   a NOT_AVAILABLE_DATA error is returned.
*
*   The line_index determines the multifield scope of the variable being get. Use the
*   get_[field|layer|phase]_id to determine this number or use 0 if it is GLOBAL.
*
*   WARNING: Changing the contents returned by this function has **UNDEFINED BEHAVIOR**.
*   The user must **NEVER** change the contents returned by this function.
*/
typedef int (*get_simulation_array_func)(
    void* ctx,
    double** out,
    char* variable_name,
    struct VariableScope var_scope,
    int line_index,
    int* size
);
get_simulation_array_func get_simulation_array;

/**
*   get_simulation_quantity
*
*   Get the current contents of a given secondary variable (For a single quantity).
*   A secondary variable is any variable calculated in the solver iterative procedure.
*   Note that not all variables are available at any time. If a given variable is not available,
*   a NOT_AVAILABLE_DATA error is returned.
*/
typedef int (*get_simulation_quantity_func)(
    void* ctx,
    double* out,
    enum TimestepScope ts_scope,
    char* variable_name_c
);
get_simulation_quantity_func get_simulation_quantity;

/**
*   get_wall_interfaces_temperature
*
*   Get the wall interface temperature for a given control volume. Each control volume has an array
*   of temperatures, one for each wall layer. The temperatures are given in the wall interfaces.
*/
typedef int (*get_wall_interfaces_temperature_func)(
    void* ctx,
    double** out,
    int control_volume,
    enum TimestepScope ts_scope,
    int* size
);
get_wall_interfaces_temperature_func get_wall_interfaces_temperature;


/**
*   get_flow_pattern
*
*   Get the flow pattern for each control volume.
*/
typedef int (*get_flow_pattern_func)(
    void* ctx,
    int** out,
    enum GridScope grid_scope,
    enum TimestepScope ts_scope,
    int* size
);
get_flow_pattern_func get_flow_pattern;


#endif
