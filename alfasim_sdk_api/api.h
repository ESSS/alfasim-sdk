#ifndef _H_ALFASIM_SDK_API_PTRS
#define _H_ALFASIM_SDK_API_PTRS

#include <alfasim_sdk_api/commom.h>

#if defined(_WIN32) && defined(_ALFASIM_EXPORT_SYMBOLS)
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT
#endif

DLL_EXPORT int set_plugin_data(void* ctx, const char* plugin_name, void* data);
DLL_EXPORT int get_plugin_data(void* ctx, const char* plugin_name, void** out);

DLL_EXPORT int get_plugin_input_data_boolean(void* ctx, const char* plugin_name, const char* var_name, bool* out);
DLL_EXPORT int get_plugin_input_data_enum(void* ctx, const char* plugin_name, const char* var_name, int* out);
DLL_EXPORT int get_plugin_input_data_quantity(void* ctx, const char* plugin_name, const char* var_name, double* out);
DLL_EXPORT int get_plugin_input_data_string(void* ctx, const char* plugin_name, const char* var_name, int size, char* out);
DLL_EXPORT int get_plugin_input_data_string_size(void* ctx, const char* plugin_name, const char* var_name, int* out);

DLL_EXPORT int get_plugin_variable(void* ctx, const char* variable_name, int line_index, int* size, void** out);

#endif
