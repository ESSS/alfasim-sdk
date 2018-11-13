#ifndef _H_ALFASIM_SDK_API_PTRS
#define _H_ALFASIM_SDK_API_PTRS

#if defined(_WIN32) && defined(_ALFASIM_EXPORT_SYMBOLS)
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT
#endif

enum error_code
{
    UNDEFINED_DATA=-2,
    NOT_IMPLEMENTED=-1,
    SUCCESS = 0,
};

DLL_EXPORT int set_plugin_data(void* ctx, const char* plugin_name, void* data);
DLL_EXPORT int get_plugin_data(void* ctx, const char* plugin_name, void** out);

DLL_EXPORT int get_plugin_input_data_bool(void* ctx, const char* plugin_name, const char* var_name, bool* out);
DLL_EXPORT int get_plugin_input_data_int(void* ctx, const char* plugin_name, const char* var_name, int* out);
DLL_EXPORT int get_plugin_input_data_double(void* ctx, const char* plugin_name, const char* var_name, double* out);

#endif
