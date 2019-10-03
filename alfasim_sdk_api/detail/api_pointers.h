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
typedef int (*get_primary_field_id_of_phase_func)(void* ctx, int* out, const char* name);
typedef int (*get_phase_id_func)(void* ctx, int* out, const char* name);
typedef int (*get_layer_id_func)(void* ctx, int* out, const char* name);
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
    char* variable_name,
    struct VariableScope var_scope,
    int line_index,
    int* size
);
typedef int (*get_simulation_tracer_array_func)(
    void* ctx,
    double** out,
    char* variable_name,
    struct VariableScope var_scope,
    int tracer_index,
    int line_index,
    int* size
);
typedef int (*get_simulation_quantity_func)(
    void* ctx,
    double* out,
    enum TimestepScope ts_scope,
    char* variable_name_c
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
typedef int (*get_wall_layer_id_func)(void* ctx, int control_volume, const char* material_name, int* out);
typedef int (*set_wall_layer_property_func)(void* ctx, int control_volume, int wall_layer_id, enum WallLayerProperty property_id, double new_value);
typedef int (*get_plugin_input_data_multiplereference_selected_size_func)(void* ctx, int* indexes_size, const char* plugin_id, const char* var_name);

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

    get_plugin_input_data_reference_func get_plugin_input_data_reference;

    get_plugin_input_data_table_quantity_func get_plugin_input_data_table_quantity;

    get_plugin_variable_func get_plugin_variable;

    get_field_id_func get_field_id;
    get_primary_field_id_of_phase_func get_primary_field_id_of_phase;
    get_phase_id_func get_phase_id;
    get_layer_id_func get_layer_id;

    get_state_variable_array_func get_state_variable_array;
    get_simulation_array_func get_simulation_array;

    /**
    *   get_simulation_tracer_array
    *
    *   Get the current contents of a given tracer mass fraction (For an array data pointer).
    *   A  tracer mass fraction is calculated in the extra solver iterative procedure.
    *   Note that not all tracer mass fraction are available at any time.
    *   If a given tracer mass fraction (in an inexistent field) is not available,
    *   a NOT_AVAILABLE_DATA error is returned.
    *
    *   The line_index determines the multifield scope of the tracer mass fraction being get.
    *   Use the get_[field|phase]_id to determine this number or use 0 if it is GLOBAL.
    *   The tracer_index determines the tracer that the mass fraction is being get.
    *   Use the get_tracer_id to determine this number.
    *
    *   WARNING: Changing the contents returned by this function has **UNDEFINED BEHAVIOR**.
    *   The user must **NEVER** change the contents returned by this function.
    */
    get_simulation_tracer_array_func get_simulation_tracer_array;

    /**
    *   get_simulation_quantity
    *
    *   Get the current contents of a given secondary variable (For a single quantity).
    *   A secondary variable is any variable calculated in the solver iterative procedure.
    *   Note that not all variables are available at any time. If a given variable is not available,
    *   a NOT_AVAILABLE_DATA error is returned.
    */
    get_simulation_quantity_func get_simulation_quantity;

    /**
    *   get_wall_interfaces_temperature
    *
    *   Get the wall interface temperature for a given control volume. Each control volume has an array
    *   of temperatures, one for each wall layer. The temperatures are given in the wall interfaces.
    */
    get_wall_interfaces_temperature_func get_wall_interfaces_temperature;


    /**
    *   get_flow_pattern
    *
    *   Get the flow pattern for each control volume.
    */
    get_flow_pattern_func get_flow_pattern;


    /**
    *   get_tracer_id
    *
    *   Retrieves the tracer ID given a tracer reference. A tracer reference may be obtained from the
    *   user input data (See get_plugin_input_data_reference API function for an example).
    */
    get_tracer_id_func get_tracer_id;


    /**
    *   get_tracer_name_size
    *
    *   Retrieves the size of the tracer name, given a tracer reference. A tracer reference may be
    *   obtained from the user input data (See get_plugin_input_data_reference API function for an
    *   example).
    */
    get_tracer_name_size_func get_tracer_name_size;


    /**
    *   get_tracer_name
    *
    *   Retrieves the tracer name, given a tracer reference. The tracer_name parameter must be a valid
    *   and pre-allocated memory region where the name string will be copied to. A tracer reference may
    *   be obtained from the user input data (See get_plugin_input_data_reference API function for an
    *   example).
    *
    *   Example usage:
    *   int tracer_name_size = -1;
    *   errcode = get_tracer_name_size(ctx, &tracer_name_size, tracer_ref);
    *
    *   char* tracer_name = (char*)malloc(sizeof(char) * tracer_name_size);
    *   errcode = get_tracer_name(ctx, tracer_name, tracer_ref, tracer_name_size);
    *   std::cout << "TRACER NAME: " << tracer_name << std::endl;
    *   free(tracer_name);
    */
    get_tracer_name_func get_tracer_name;


    /**
    *   get_tracer_ref_by_name
    *
    *   Get the tracer reference for a given tracer name. This function is important to obtain the
    *   tracer reference of a user defined tracer added by the plugin.
    */
    get_tracer_ref_by_name_func get_tracer_ref_by_name;


    /**
    *   get_tracer_partition_coefficient
    *
    *   Get the partition coefficient input data for a given tracer reference. The phase_id must also
    *   be given (See get_phase_id API function). A tracer reference may be obtained from the user
    *   input data (See get_plugin_input_data_reference API function for an example).
    */
    get_tracer_partition_coefficient_func get_tracer_partition_coefficient;


    /**
    *   get_wall_layer_id
    *
    *   Get the wall layer id in the given control volume, with a given material name.
    *   The layer id is output in the "out" variable.
    */
    get_wall_layer_id_func get_wall_layer_id;

    /**
    *   set_wall_layer_property
    *
    *   Set a property in the given wall layer (Use get_wall_layer_id to get it), in a given control
    *   volume. Please note that the new value is assumed to be physical, as no sanity check is
    *   performed by the solver.
    */
    set_wall_layer_property_func set_wall_layer_property;


    /**
    *   get_plugin_input_data_multiplereference_selected_size
    *
    *   Get the number of selected references in a multiple-reference selection. User should be able to
    *   iterate over the selections to get information.
    *
    *   Example usage:
    *        int errcode = -1;
    *        int indexes_size = -1;
    *        errcode = get_plugin_input_data_multiplereference_selected_size(
    *            ctx, &indexes_size, plugin_id, "Model.internal_multiple_reference");
    *
    *        for (int i = 0; i < indexes_size; ++i) {
    *            auto value = -1.0;
    *            auto reference_str = std::string(
    *                "Model.internal_multiple_reference[" + std::to_string(i) + "]->quantity");
    *
    *            errcode = get_plugin_input_data_quantity(
    *                ctx, &value, plugin_id, reference_str.c_str());
    *            }
    *        }
    *
    */
    get_plugin_input_data_multiplereference_selected_size_func get_plugin_input_data_multiplereference_selected_size;
};

#endif
