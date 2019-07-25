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
DLL_EXPORT int get_plugin_input_data_filepath(void* ctx, char* out, const char* plugin_name, const char* var_name, int size);
DLL_EXPORT int get_plugin_input_data_filepath_size(void* ctx, int* out, const char* plugin_name, const char* var_name);
DLL_EXPORT int get_plugin_input_data_reference(void* ctx, void** out, const char* plugin_name, const char* var_name);

DLL_EXPORT int get_plugin_variable(void* ctx, void** out, const char* variable_name, int line_index, enum TimestepScope ts_scope, int* size);

DLL_EXPORT int get_field_id(void* ctx, int* out, const char* name);
DLL_EXPORT int get_primary_field_id_of_phase(void* ctx, int* out, const char* name);
DLL_EXPORT int get_phase_id(void* ctx, int* out, const char* name);
DLL_EXPORT int get_layer_id(void* ctx, int* out, const char* name);
DLL_EXPORT int get_state_variable_array(
    void* ctx,
    double** out,
    enum StateVariable state_var,
    int field_index,
    int* size
);
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
DLL_EXPORT int get_plugin_input_data_table_quantity(
    void* ctx,
    double** out,
    int* size,
    const char* column_id,
    const char* plugin_name,
    const char* var_name
);

DLL_EXPORT int get_tracer_id(void* ctx, int* tracer_id, void* reference);
DLL_EXPORT int get_tracer_name_size(void* ctx, int* tracer_name_size, void* reference);
DLL_EXPORT int get_tracer_name(void* ctx, char* out, void* reference, int size);
DLL_EXPORT int get_tracer_ref_by_name(void* ctx, void** reference, const char* tracer_name, const char* plugin_name);
DLL_EXPORT int get_tracer_partition_coefficient(void* ctx, double* out, void* reference, int phase_id);

DLL_EXPORT int get_wall_layer_id(void* ctx, int control_volume, const char* material_name, int* out);
DLL_EXPORT int set_wall_layer_property(void* ctx, int control_volume, int wall_layer_id, enum WallLayerProperty property_id, double new_value);

DLL_EXPORT int get_plugin_input_data_multiplereference_selected_size(void* ctx, int* indexes_size, const char* plugin_name, const char* var_name);

#endif
