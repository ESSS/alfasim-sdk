#ifndef _H_ALFASIM_SDK_BOOTSTRAP_LINUX
#define _H_ALFASIM_SDK_BOOTSTRAP_LINUX

#include <alfasim_sdk_api/detail/api_pointers.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define MAX_PATH 4096

struct alfasim_sdk_bootstrap {
    alfasim_sdk_bootstrap()
    {
        char SO_FILENAME[] = "/alfasim_plugins_api.so";

        // Extract the folder from the executable's full path
        char current_exe_dir[MAX_PATH];
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
        this->m_handle = dlopen(full_filepath, RTLD_LAZY);

        // Register alfasim API
        set_plugin_data = (set_plugin_data_func)dlsym(this->m_handle, "set_plugin_data");
        get_plugin_data = (get_plugin_data_func)dlsym(this->m_handle, "get_plugin_data");
        get_plugin_input_data_boolean = (get_plugin_input_data_boolean_func)dlsym(this->m_handle, "get_plugin_input_data_boolean");
        get_plugin_input_data_enum = (get_plugin_input_data_enum_func)dlsym(this->m_handle, "get_plugin_input_data_enum");
        get_plugin_input_data_quantity = (get_plugin_input_data_quantity_func)dlsym(this->m_handle, "get_plugin_input_data_quantity");
        get_plugin_input_data_string = (get_plugin_input_data_string_func)dlsym(this->m_handle, "get_plugin_input_data_string");
        get_plugin_input_data_string_size = (get_plugin_input_data_string_size_func)dlsym(this->m_handle, "get_plugin_input_data_string_size");
        get_plugin_input_data_filepath = (get_plugin_input_data_filepath_func)dlsym(this->m_handle, "get_plugin_input_data_filepath");
        get_plugin_input_data_filepath_size = (get_plugin_input_data_filepath_size_func)dlsym(this->m_handle, "get_plugin_input_data_filepath_size");
        get_plugin_input_data_reference = (get_plugin_input_data_reference_func)dlsym(this->m_handle, "get_plugin_input_data_reference");
        get_plugin_variable = (get_plugin_variable_func)dlsym(this->m_handle, "get_plugin_variable");
        get_field_id = (get_field_id_func)dlsym(this->m_handle, "get_field_id");
        get_primary_field_id_of_phase = (get_field_id_func)dlsym(this->m_handle, "get_primary_field_id_of_phase");
        get_phase_id = (get_phase_id_func)dlsym(this->m_handle, "get_phase_id");
        get_layer_id = (get_layer_id_func)dlsym(this->m_handle, "get_layer_id");
        get_state_variable_array = (get_state_variable_array_func)dlsym(this->m_handle, "get_state_variable_array");
        get_simulation_array = (get_simulation_array_func)dlsym(this->m_handle, "get_simulation_array");
        get_simulation_tracer_array = (get_simulation_tracer_array_func)dlsym(this->m_handle, "get_simulation_tracer_array");
        get_simulation_quantity = (get_simulation_quantity_func)dlsym(this->m_handle, "get_simulation_quantity");
        get_wall_interfaces_temperature = (get_wall_interfaces_temperature_func)dlsym(this->m_handle, "get_wall_interfaces_temperature");
        get_flow_pattern = (get_flow_pattern_func)dlsym(this->m_handle, "get_flow_pattern");
        get_plugin_input_data_table_quantity = (get_plugin_input_data_table_quantity_func)dlsym(this->m_handle, "get_plugin_input_data_table_quantity");
        get_tracer_id = (get_tracer_id_func)dlsym(this->m_handle, "get_tracer_id");
        get_tracer_name_size = (get_tracer_name_size_func)dlsym(this->m_handle, "get_tracer_name_size");
        get_tracer_name = (get_tracer_name_func)dlsym(this->m_handle, "get_tracer_name");
        get_tracer_ref_by_name = (get_tracer_ref_by_name_func)dlsym(this->m_handle, "get_tracer_ref_by_name");
        get_tracer_partition_coefficient = (get_tracer_partition_coefficient_func)dlsym(this->m_handle, "get_tracer_partition_coefficient");
        get_wall_layer_id = (get_wall_layer_id_func)dlsym(this->m_handle, "get_wall_layer_id");
        set_wall_layer_property = (set_wall_layer_property_func)dlsym(this->m_handle, "set_wall_layer_property");
    }

    ~alfasim_sdk_bootstrap()
    {
        dlclose(this->m_handle);
    }

    void* m_handle;
};
alfasim_sdk_bootstrap _;

#endif
