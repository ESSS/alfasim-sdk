#ifndef _H_ALFASIM_SDK_API
#define _H_ALFASIM_SDK_API

typedef int (*set_plugin_data_func)(void*, const char*, void*);
set_plugin_data_func set_plugin_data;

typedef int (*get_plugin_data_func)(void*, const char*, void**);
get_plugin_data_func get_plugin_data;

#endif
