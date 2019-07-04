#ifndef _H_ALFASIM_SDK_BOOTSTRAP_WIN
#define _H_ALFASIM_SDK_BOOTSTRAP_WIN

#include <alfasim_sdk_api/detail/api_pointers.h>
#include <windows.h>
#include <stdlib.h>
#include <strsafe.h>

struct alfasim_sdk_bootstrap {
    alfasim_sdk_bootstrap()
    {
        WCHAR DLL_FILENAME[] = L"/alfasim_plugins_api.dll";

        // Extract the folder from the executable's full path
        WCHAR current_exe_dir[MAX_PATH];
        {
            WCHAR current_exe_fullpath[MAX_PATH];
            GetModuleFileNameW(NULL, current_exe_fullpath, MAX_PATH);
            int size; for (size = 0; current_exe_fullpath[size] != '\0'; ++size);
            if (size > 0) {
                int i = size;
                int j = 0;
                for (; i > 0 && current_exe_fullpath[i] != '\\' && current_exe_fullpath[i] != '/'; --i);
                for (j = 0; j < i; j++) {
                    current_exe_dir[j] = current_exe_fullpath[j];
                }
                current_exe_dir[j] = '\0';
            }
        }

        // Extract the folder from the environment variable
        WCHAR *executable_dir_from_env = NULL;
        size_t _len = 0;
        _wdupenv_s(&executable_dir_from_env, &_len, L"ALFASIM_PATH");

        // Find the alfasim installation path: Prefer the environment variable ALFASIM_PATH, but, if not found,
        // try the same path as the executable
        WCHAR *alfasim_executable_dir;
        if (executable_dir_from_env != NULL) {
            alfasim_executable_dir = executable_dir_from_env;
        } else {
            alfasim_executable_dir = current_exe_dir;
        }

        // Load shared object
        WCHAR full_filepath[MAX_PATH];
        full_filepath[0] = '\0';
        StringCchCatW(full_filepath, MAX_PATH, alfasim_executable_dir);
        StringCchCatW(full_filepath, MAX_PATH, DLL_FILENAME);
        this->dllHandle = LoadLibraryW(full_filepath);

        // Register alfasim API
        set_plugin_data = (set_plugin_data_func)GetProcAddress(this->dllHandle, "set_plugin_data");
        get_plugin_data = (get_plugin_data_func)GetProcAddress(this->dllHandle, "get_plugin_data");
        get_plugin_input_data_boolean = (get_plugin_input_data_boolean_func)GetProcAddress(this->dllHandle, "get_plugin_input_data_boolean");
        get_plugin_input_data_enum = (get_plugin_input_data_enum_func)GetProcAddress(this->dllHandle, "get_plugin_input_data_enum");
        get_plugin_input_data_quantity = (get_plugin_input_data_quantity_func)GetProcAddress(this->dllHandle, "get_plugin_input_data_quantity");
        get_plugin_input_data_string = (get_plugin_input_data_string_func)GetProcAddress(this->dllHandle, "get_plugin_input_data_string");
        get_plugin_input_data_string_size = (get_plugin_input_data_string_size_func)GetProcAddress(this->dllHandle, "get_plugin_input_data_string_size");
        get_plugin_input_data_reference = (get_plugin_input_data_reference_func)GetProcAddress(this->dllHandle, "get_plugin_input_data_reference");
        get_plugin_variable = (get_plugin_variable_func)GetProcAddress(this->dllHandle, "get_plugin_variable");
        get_field_id = (get_field_id_func)GetProcAddress(this->dllHandle, "get_field_id");
        get_primary_field_id_of_phase = (get_primary_field_id_of_phase_func)GetProcAddress(this->dllHandle, "get_primary_field_id_of_phase");
        get_phase_id = (get_phase_id_func)GetProcAddress(this->dllHandle, "get_phase_id");
        get_layer_id = (get_layer_id_func)GetProcAddress(this->dllHandle, "get_layer_id");
        get_state_variable_array = (get_state_variable_array_func)GetProcAddress(this->dllHandle, "get_state_variable_array");
        get_simulation_array = (get_simulation_array_func)GetProcAddress(this->dllHandle, "get_simulation_array");
        get_simulation_tracer_array = (get_simulation_tracer_array_func)GetProcAddress(this->dllHandle, "get_simulation_tracer_array");
        get_simulation_quantity = (get_simulation_quantity_func)GetProcAddress(this->dllHandle, "get_simulation_quantity");
        get_wall_interfaces_temperature = (get_wall_interfaces_temperature_func)GetProcAddress(this->dllHandle, "get_wall_interfaces_temperature");
        get_flow_pattern = (get_flow_pattern_func)GetProcAddress(this->dllHandle, "get_flow_pattern");
        get_plugin_input_data_table_quantity = (get_plugin_input_data_table_quantity_func)GetProcAddress(this->dllHandle, "get_plugin_input_data_table_quantity");
        get_tracer_id = (get_tracer_id_func)GetProcAddress(this->dllHandle, "get_tracer_id");
        get_tracer_name_size = (get_tracer_name_size_func)GetProcAddress(this->dllHandle, "get_tracer_name_size");
        get_tracer_name = (get_tracer_name_func)GetProcAddress(this->dllHandle, "get_tracer_name");
        get_tracer_partition_coefficient = (get_tracer_partition_coefficient_func)GetProcAddress(this->dllHandle, "get_tracer_partition_coefficient");
        get_wall_layer_id = (get_wall_layer_id_func)GetProcAddress(this->dllHandle, "get_wall_layer_id");
        set_wall_layer_property = (set_wall_layer_property_func)GetProcAddress(this->dllHandle, "set_wall_layer_property");

        free(executable_dir_from_env);
    }

    ~alfasim_sdk_bootstrap()
    {
        FreeLibrary(this->dllHandle);
    }

    HINSTANCE dllHandle = NULL;
};
alfasim_sdk_bootstrap _;

#endif
