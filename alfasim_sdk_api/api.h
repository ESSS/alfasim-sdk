#ifndef _H_ALFASIM_SDK_API_PTRS
#define _H_ALFASIM_SDK_API_PTRS

#include <alfasim_sdk_api/common.h>

#if defined(_WIN32) && defined(_ALFASIM_EXPORT_SYMBOLS)
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT
#endif

DLL_EXPORT int set_plugin_data(void* ctx, const char* plugin_name, void* data);
DLL_EXPORT int get_plugin_data(void* ctx, void** out, const char* plugin_name);

DLL_EXPORT int get_plugin_input_data_boolean(void* ctx, bool* out, const char* plugin_name, const char* var_name);
DLL_EXPORT int get_plugin_input_data_enum(void* ctx, int* out, const char* plugin_name, const char* var_name);
DLL_EXPORT int get_plugin_input_data_quantity(void* ctx, double* out, const char* plugin_name, const char* var_name);
DLL_EXPORT int get_plugin_input_data_string(void* ctx, char* out, const char* plugin_name, const char* var_name, int size);
DLL_EXPORT int get_plugin_input_data_string_size(void* ctx, int* out, const char* plugin_name, const char* var_name);

DLL_EXPORT int get_plugin_variable(void* ctx, void** out, const char* variable_name, int line_index, int* size);

DLL_EXPORT int get_field_id(void* ctx, int* out, const char* name);
DLL_EXPORT int get_primary_field_id_of_phase(void* ctx, int* out, const char* name);
DLL_EXPORT int get_phase_id(void* ctx, int* out, const char* name);
DLL_EXPORT int get_layer_id(void* ctx, int* out, const char* name);
DLL_EXPORT int get_simulation_array(
    void* ctx,
    double** out,
    char* variable_name,
    int line_index,
    int timestep,
    int* size
);
DLL_EXPORT int get_simulation_quantity(
    void* ctx,
    double* out,
    char* variable_name_c,
    int timestep
);
DLL_EXPORT int get_wall_interfaces_temperature(
    void* ctx,
    double** out,
    int control_volume,
    int timestep,
    int* size
);
DLL_EXPORT int get_number_of_control_volumes(void* ctx, int* out);

#endif
