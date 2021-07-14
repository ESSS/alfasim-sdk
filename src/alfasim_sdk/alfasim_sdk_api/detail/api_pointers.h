#ifndef _H_ALFASIM_SDK_API
#define _H_ALFASIM_SDK_API

#if defined(_WIN32)
#include <windows.h>
#endif

typedef int (*set_plugin_data_func)(void*, const char*, void*, int);
typedef int (*get_thread_id_func)(void*, int*);
typedef int (*get_plugin_input_data_boolean_func)(void*, bool*, const char*, const char*);
typedef int (*get_plugin_input_data_enum_func)(void*, int*, const char*, const char*);
typedef int (*get_plugin_input_data_quantity_func)(void*, double*, const char*, const char*);
typedef int (*get_plugin_input_data_file_content_func)(void*, char*, const char*, const char*, int);
typedef int (*get_plugin_input_data_file_content_size_func)(void*, int*, const char*, const char*);
typedef int (*get_plugin_input_data_string_func)(void*, char*, const char*, const char*, int);
typedef int (*get_plugin_input_data_string_size_func)(void*, int*, const char*, const char*);
typedef int (*get_plugin_input_data_reference_func)(void*, void**, const char*, const char*);
typedef int (*get_plugin_input_data_table_quantity_func)(
    void* ctx,
    double** out,
    int* size,
    const char* column_id,
    const char* plugin_id,
    const char* var_name
);
typedef int (*get_plugin_data_func)(void*, void**, const char*, int);
typedef int (*get_number_of_threads_func)(void*, int*);
typedef int (*get_plugin_variable_func)(void* ctx, void** out, const char* variable_name, int line_index, int timestep, int* size);
typedef int (*get_field_id_func)(void* ctx, int* out, const char* name);
typedef int (*get_phase_id_func)(void* ctx, int* out, const char* name);
typedef int (*get_layer_id_func)(void* ctx, int* out, const char* name);
typedef int (*get_number_of_fields_func)(void*, int*);
typedef int (*get_number_of_phases_func)(void*, int*);
typedef int (*get_number_of_layers_func)(void*, int*);
typedef int (*get_number_of_phase_pairs_func)(void*, int*);
typedef int (*get_primary_field_id_of_phase_func)(void* ctx, int* out, const char* name);
typedef int (*get_phase_id_of_fields_func)(void* ctx, int** out, int* size);
typedef int (*get_field_ids_in_layer_func)(void* ctx, int** out, int layer_id, int* size);
typedef int (*get_phase_pair_id_func)(void* ctx, int* out, int phase_0_id, int phase_1_id);
typedef int (*get_state_variable_array_func)(
    void* ctx,
    double** out,
    enum StateVariable state_var,
    int field_index,
    int* size
);
typedef int (*get_simulation_array_func)(
    void* ctx,
    double** out,
    const char* variable_name,
    struct VariableScope var_scope,
    int line_index,
    int* size
);
typedef int (*get_simulation_tracer_array_func)(
    void* ctx,
    double** out,
    const char* variable_name,
    struct VariableScope var_scope,
    int tracer_index,
    int line_index,
    int* size
);
typedef int (*get_simulation_quantity_func)(
    void* ctx,
    double* out,
    enum TimestepScope ts_scope,
    const char* variable_name_c
);
typedef int (*get_wall_interfaces_temperature_func)(
    void* ctx,
    double** out,
    int control_volume,
    enum TimestepScope ts_scope,
    int* size
);
typedef int (*get_flow_pattern_func)(
    void* ctx,
    int** out,
    enum GridScope grid_scope,
    enum TimestepScope ts_scope,
    int* size
);
typedef int (*get_tracer_id_func)(void* ctx, int* tracer_id, void* reference);
typedef int (*get_tracer_name_size_func)(void* ctx, int* tracer_name_size, void* reference);
typedef int (*get_tracer_name_func)(void* ctx, char* tracer_name, void* reference, int size);
typedef int (*get_tracer_ref_by_name_func)(void* ctx, void** reference, const char* tracer_name, const char* plugin_id);
typedef int (*get_tracer_partition_coefficient_func)(void* ctx, double* out, void* reference, int phase_id);
typedef int (*get_plugin_input_data_multiplereference_selected_size_func)(void* ctx, int* indexes_size, const char* plugin_id, const char* var_name);
typedef int (*get_input_variable_func)(void* ctx, double* out, const char* var_name, int phase_id);
typedef int (*get_ucm_fluid_geometrical_properties_func)(void* ctx, double* S_w, double* S_i, double* H, double alpha_G, double D);
typedef int (*get_relative_emulsion_viscosity_func)(void* ctx, double* out, double mu_disp, double mu_cont, double alpha_disp_in_layer, int disp_field_id, int cont_field_id);

struct ALFAsimSDK_API {
#if defined(_WIN32)
    HINSTANCE handle;
#elif defined(unix) || defined(__unix__) || defined(__unix)
    void* handle;
#else
#error "Unknown host (Alfasim SDK will only work on Linux and Windows)"
#endif

    set_plugin_data_func set_plugin_data;
    get_plugin_data_func get_plugin_data;

    get_number_of_threads_func get_number_of_threads;
    get_thread_id_func get_thread_id;

    get_plugin_input_data_boolean_func get_plugin_input_data_boolean;
    get_plugin_input_data_enum_func get_plugin_input_data_enum;
    get_plugin_input_data_quantity_func get_plugin_input_data_quantity;

    get_plugin_input_data_file_content_func get_plugin_input_data_file_content;
    get_plugin_input_data_file_content_size_func get_plugin_input_data_file_content_size;

    get_plugin_input_data_string_func get_plugin_input_data_string;
    get_plugin_input_data_string_size_func get_plugin_input_data_string_size;

    get_plugin_input_data_table_quantity_func get_plugin_input_data_table_quantity;

    get_plugin_input_data_reference_func get_plugin_input_data_reference;
    get_plugin_input_data_multiplereference_selected_size_func get_plugin_input_data_multiplereference_selected_size;

    get_plugin_variable_func get_plugin_variable;

    get_field_id_func get_field_id;
    get_phase_id_func get_phase_id;
    get_layer_id_func get_layer_id;
    get_number_of_fields_func get_number_of_fields;
    get_number_of_phases_func get_number_of_phases;
    get_number_of_layers_func get_number_of_layers;
    get_number_of_phase_pairs_func get_number_of_phase_pairs;
    get_primary_field_id_of_phase_func get_primary_field_id_of_phase;
    get_phase_id_of_fields_func get_phase_id_of_fields;
    get_field_ids_in_layer_func get_field_ids_in_layer;
    get_phase_pair_id_func get_phase_pair_id;

    get_state_variable_array_func get_state_variable_array;
    get_simulation_array_func get_simulation_array;
    get_simulation_tracer_array_func get_simulation_tracer_array;
    get_simulation_quantity_func get_simulation_quantity;

    get_flow_pattern_func get_flow_pattern;
    get_flow_pattern_func get_liqliq_flow_pattern;

    get_tracer_id_func get_tracer_id;
    get_tracer_name_size_func get_tracer_name_size;
    get_tracer_name_func get_tracer_name;
    get_tracer_ref_by_name_func get_tracer_ref_by_name;
    get_tracer_partition_coefficient_func get_tracer_partition_coefficient;

    get_wall_interfaces_temperature_func get_wall_interfaces_temperature;

    get_input_variable_func get_ucm_friction_factor_input_variable;
    get_ucm_fluid_geometrical_properties_func get_ucm_fluid_geometrical_properties;
    get_input_variable_func get_liq_liq_flow_pattern_input_variable;
    get_input_variable_func get_liquid_effective_viscosity_input_variable;
    get_input_variable_func get_gas_liq_surface_tension_input_variable;
    get_input_variable_func get_liq_liq_shear_force_per_volume_input_variable;

    get_relative_emulsion_viscosity_func get_relative_emulsion_viscosity;

};

#endif
