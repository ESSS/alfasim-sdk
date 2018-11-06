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

#endif
