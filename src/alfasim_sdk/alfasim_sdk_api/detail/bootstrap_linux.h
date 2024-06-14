#ifndef _H_ALFASIM_SDK_BOOTSTRAP_LINUX
#define _H_ALFASIM_SDK_BOOTSTRAP_LINUX

#include <alfasim_sdk_api/detail/api_pointers.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define MAX_PATH_SIZE 32767

/***
Load ALFAsim-SDK API shared object (so file).

@param[out] api ALFAsim-SDK API.
@return An #sdk_load_error_code value.

***/
inline int alfasim_sdk_open(ALFAsimSDK_API* api)
{
    if (api->handle != nullptr) {
        return SDK_ALREADY_OPEN_ERROR;
    }

    char SO_FILENAME[] = "/alfasim_plugins_api.so";

    // Extract the folder from the executable's full path
    char current_exe_dir[MAX_PATH_SIZE];
    getcwd(current_exe_dir, sizeof(current_exe_dir));

    // Extract the folder from the environment variable
    char* executable_dir_from_env = getenv("ALFASIM_PATH");

    // Find the alfasim installation path: Prefer the environment variable ALFASIM_PATH, but, if not found,
    // try the same path as the executable
    char *alfasim_executable_dir;
    if (executable_dir_from_env != NULL) {
        alfasim_executable_dir = executable_dir_from_env;
    } else {
        alfasim_executable_dir = current_exe_dir;
    }

    // Load shared object
    char *full_filepath = NULL;
    asprintf(&full_filepath, "%s%s", alfasim_executable_dir, SO_FILENAME);

    // https://www.man7.org/linux/man-pages/man3/dlopen.3.html
    // > If dlopen() fails for any reason, it returns NULL.
    api->handle = dlopen(full_filepath, RTLD_LAZY);
    free(full_filepath);
    if (api->handle == NULL) {
        return SDK_FAILED_TO_LOAD_DLL;
    }

    // https://man7.org/linux/man-pages/man3/dlsym.3.html
    // > In unusual cases (see NOTES) the value of the symbol could actually be NULL.  Therefore,
    // > a NULL return from dlsym() need not indicate an error.  The correct way to distinguish an
    // > error from a symbol whose value is NULL is to call dlerror(3) to clear any old error
    // > conditions, then call dlsym(), and then call dlerror(3) again, saving its return value
    // > into a variable, and check whether this saved value is not NULL.
    #define LOAD_SDK_PROC_MAP_TYPE(func_name, func_type) {\
        dlerror();\
        api->func_name = (func_type)dlsym(api->handle, #func_name);\
        char *last_error = dlerror();\
        if (last_error != NULL) {\
            dlclose(api->handle);\
            api->handle = nullptr;\
            return SDK_FAILED_TO_LOAD_FUNCTION;\
        }\
    }
    #define LOAD_SDK_PROC(func_name) LOAD_SDK_PROC_MAP_TYPE(func_name, func_name ## _func)

    // Register alfasim API
    LOAD_SDK_PROC(set_plugin_data)
    LOAD_SDK_PROC(get_plugin_data)
    LOAD_SDK_PROC(get_number_of_threads)
    LOAD_SDK_PROC(get_thread_id)
    LOAD_SDK_PROC(get_plugin_input_data_boolean)
    LOAD_SDK_PROC(get_plugin_input_data_enum)
    LOAD_SDK_PROC(get_plugin_input_data_quantity)
    LOAD_SDK_PROC(get_plugin_input_data_string)
    LOAD_SDK_PROC(get_plugin_input_data_string_size)
    LOAD_SDK_PROC(get_plugin_input_data_file_content)
    LOAD_SDK_PROC(get_plugin_input_data_file_content_size)
    LOAD_SDK_PROC(get_plugin_input_data_reference)
    LOAD_SDK_PROC(get_plugin_variable)
    LOAD_SDK_PROC(get_field_id)
    LOAD_SDK_PROC(get_phase_id)
    LOAD_SDK_PROC(get_layer_id)
    LOAD_SDK_PROC(get_number_of_fields)
    LOAD_SDK_PROC(get_number_of_phases)
    LOAD_SDK_PROC(get_number_of_layers)
    LOAD_SDK_PROC(get_number_of_phase_pairs)
    LOAD_SDK_PROC_MAP_TYPE(get_primary_field_id_of_phase, get_field_id_func)
    LOAD_SDK_PROC(get_phase_id_of_fields)
    LOAD_SDK_PROC(get_field_ids_in_layer)
    LOAD_SDK_PROC(get_phase_pair_id)
    LOAD_SDK_PROC(get_state_variable_array)
    LOAD_SDK_PROC(get_simulation_array)
    LOAD_SDK_PROC(get_simulation_tracer_array)
    LOAD_SDK_PROC(get_simulation_quantity)
    LOAD_SDK_PROC(get_wall_interfaces_temperature)
    LOAD_SDK_PROC(get_flow_pattern)
    LOAD_SDK_PROC_MAP_TYPE(get_liqliq_flow_pattern, get_flow_pattern_func)
    LOAD_SDK_PROC(get_deposition_thickness)
    LOAD_SDK_PROC(get_plugin_input_data_table_quantity)
    LOAD_SDK_PROC(get_tracer_id)
    LOAD_SDK_PROC(get_tracer_name_size)
    LOAD_SDK_PROC(get_tracer_name)
    LOAD_SDK_PROC(get_tracer_ref_by_name)
    LOAD_SDK_PROC(get_tracer_partition_coefficient)
    LOAD_SDK_PROC(get_plugin_input_data_multiplereference_selected_size)
    LOAD_SDK_PROC_MAP_TYPE(get_ucm_friction_factor_input_variable, get_input_variable_func)
    LOAD_SDK_PROC(get_ucm_fluid_geometrical_properties)
    LOAD_SDK_PROC_MAP_TYPE(get_liq_liq_flow_pattern_input_variable, get_input_variable_func)
    LOAD_SDK_PROC_MAP_TYPE(get_liquid_effective_viscosity_input_variable, get_input_variable_func)
    LOAD_SDK_PROC_MAP_TYPE(get_gas_liq_surface_tension_input_variable, get_input_variable_func)
    LOAD_SDK_PROC_MAP_TYPE(get_liq_liq_shear_force_per_volume_input_variable, get_input_variable_func)
    LOAD_SDK_PROC(get_relative_emulsion_viscosity)

    return SDK_OK;
}

inline void alfasim_sdk_close(ALFAsimSDK_API* api)
{
    if (api->handle != nullptr){
        dlclose(api->handle);
        api->handle = nullptr;
    }
}

#endif
