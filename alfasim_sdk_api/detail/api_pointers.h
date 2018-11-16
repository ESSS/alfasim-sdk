#ifndef _H_ALFASIM_SDK_API
#define _H_ALFASIM_SDK_API

typedef int (*set_plugin_data_func)(void*, const char*, void*);
set_plugin_data_func set_plugin_data;

typedef int (*get_plugin_data_func)(void*, const char*, void**);
get_plugin_data_func get_plugin_data;

typedef int (*get_plugin_input_data_bool_func)(void*, const char*, const char*, bool*);
get_plugin_input_data_bool_func get_plugin_input_data_bool;

typedef int (*get_plugin_input_data_int_func)(void*, const char*, const char*, int*);
get_plugin_input_data_int_func get_plugin_input_data_int;

typedef int (*get_plugin_input_data_double_func)(void*, const char*, const char*, double*);
get_plugin_input_data_double_func get_plugin_input_data_double;

#endif
