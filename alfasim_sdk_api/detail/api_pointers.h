#ifndef _H_ALFASIM_SDK_API
#define _H_ALFASIM_SDK_API

typedef int (*set_plugin_data_func)(void*, const char*, void*);
set_plugin_data_func set_plugin_data;


/**
*   get_plugin_input_data
*   This function is used to get the data provided from the user
*/
typedef int (*get_plugin_data_func)(void*, const char*, void**);
get_plugin_data_func get_plugin_data;


/**
*   get_plugin_input_data_boolean()
*
*   Get the data provided from the user on a Boolean input field.
*       For more detail about the Boolean input field check alfasim_sdk.types.Boolean
*/
typedef int (*get_plugin_input_data_boolean_func)(void*, const char*, const char*, bool*);
get_plugin_input_data_boolean_func get_plugin_input_data_boolean;


/**
*   get_plugin_input_data_enum()
*
*   Get the data provided from the user on a Enum input field.
*       For more detail about the Enum input field check alfasim_sdk.types.Enum
*/
typedef int (*get_plugin_input_data_enum_func)(void*, const char*, const char*, int*);
get_plugin_input_data_enum_func get_plugin_input_data_enum;

/**
*   get_plugin_input_data_quantity()
*
*   Get the data provided from the user on a Quantity input field.
*       For more detail about the quantity input field check alfasim_sdk.types.Quantity
*/
typedef int (*get_plugin_input_data_quantity_func)(void*, const char*, const char*, double*);
get_plugin_input_data_quantity_func get_plugin_input_data_quantity;


typedef int (*get_plugin_variable_func)(void* ctx, const char* variable_name, int line_index, int* size, void** out);
get_plugin_variable_func get_plugin_variable;

#endif
