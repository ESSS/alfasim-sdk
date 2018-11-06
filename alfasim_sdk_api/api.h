#ifndef _H_ALFASIM_SDK_API_PTRS
#define _H_ALFASIM_SDK_API_PTRS

enum error_code
{
    UNKNOWN_VARIABLE_NAME=-2,
    NOT_IMPLEMENTED=-1,
    SUCCESS = 0,
};

int set_plugin_data(void* ctx, const char* plugin_name, void* data);

#endif
