#ifndef _H_ALFASIM_SDK_BOOTSTRAP_WIN
#define _H_ALFASIM_SDK_BOOTSTRAP_WIN

#include <alfasim_sdk_api/detail/api_pointers.h>
#include <windows.h>
#include <stdlib.h>
#include <strsafe.h>
#include <wchar.h>
/*! @file */

#ifndef DOXYGEN_SHOULD_SKIP_THIS

#define MAX_PATH_SIZE 32767

#endif // DOXYGEN_SHOULD_SKIP_THIS

/*!
    Load ALFAsim-SDK API dll.

    @param[out] api ALFAsim-SDK API.
    @return An #sdk_load_error_code value.
*/
inline int alfasim_sdk_open(ALFAsimSDK_API* api)
{
    if (api->handle != nullptr) {
        return SDK_ALREADY_OPEN_ERROR;
    }

    WCHAR DLL_FILENAME[] = L"/alfasim_plugins_api.dll";

    // Extract the folder from the executable's full path
    WCHAR current_exe_dir[MAX_PATH_SIZE];
    {
        WCHAR current_exe_fullpath[MAX_PATH_SIZE];
        GetModuleFileNameW(NULL, current_exe_fullpath, MAX_PATH_SIZE);
        auto size = wcslen(current_exe_fullpath);
        if (size > 0) {
            auto i = size - 1;
            auto j = 0;
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

    if (wcslen(alfasim_executable_dir) + wcslen(DLL_FILENAME) > MAX_PATH_SIZE) {
        return SDK_DLL_PATH_TOO_LONG;
    }

    // Load shared object
    WCHAR full_filepath[MAX_PATH_SIZE];
    full_filepath[0] = '\0';
    StringCchCatW(full_filepath, MAX_PATH_SIZE, alfasim_executable_dir);
    StringCchCatW(full_filepath, MAX_PATH_SIZE, DLL_FILENAME);
    api->handle = LoadLibraryW(full_filepath);
    free(executable_dir_from_env);

    // Register alfasim API
    api->set_plugin_data = (set_plugin_data_func)GetProcAddress(api->handle, "set_plugin_data");
    api->get_plugin_data = (get_plugin_data_func)GetProcAddress(api->handle, "get_plugin_data");
    api->get_number_of_threads = (get_number_of_threads_func)GetProcAddress(api->handle, "get_number_of_threads");
    api->get_thread_id = (get_thread_id_func)GetProcAddress(api->handle, "get_thread_id");
    api->get_plugin_input_data_boolean = (get_plugin_input_data_boolean_func)GetProcAddress(api->handle, "get_plugin_input_data_boolean");
    api->get_plugin_input_data_enum = (get_plugin_input_data_enum_func)GetProcAddress(api->handle, "get_plugin_input_data_enum");
    api->get_plugin_input_data_quantity = (get_plugin_input_data_quantity_func)GetProcAddress(api->handle, "get_plugin_input_data_quantity");
    api->get_plugin_input_data_string = (get_plugin_input_data_string_func)GetProcAddress(api->handle, "get_plugin_input_data_string");
    api->get_plugin_input_data_string_size = (get_plugin_input_data_string_size_func)GetProcAddress(api->handle, "get_plugin_input_data_string_size");
    api->get_plugin_input_data_file_content = (get_plugin_input_data_file_content_func)GetProcAddress(api->handle, "get_plugin_input_data_file_content");
    api->get_plugin_input_data_file_content_size = (get_plugin_input_data_file_content_size_func)GetProcAddress(api->handle, "get_plugin_input_data_file_content_size");
    api->get_plugin_input_data_reference = (get_plugin_input_data_reference_func)GetProcAddress(api->handle, "get_plugin_input_data_reference");
    api->get_plugin_variable = (get_plugin_variable_func)GetProcAddress(api->handle, "get_plugin_variable");
    api->get_field_id = (get_field_id_func)GetProcAddress(api->handle, "get_field_id");
    api->get_phase_id = (get_phase_id_func)GetProcAddress(api->handle, "get_phase_id");
    api->get_layer_id = (get_layer_id_func)GetProcAddress(api->handle, "get_layer_id");
    api->get_number_of_fields = (get_number_of_fields_func)GetProcAddress(api->handle, "get_number_of_fields");
    api->get_number_of_phases = (get_number_of_phases_func)GetProcAddress(api->handle, "get_number_of_phases");
    api->get_number_of_layers = (get_number_of_layers_func)GetProcAddress(api->handle, "get_number_of_layers");
    api->get_number_of_phase_pairs = (get_number_of_phase_pairs_func)GetProcAddress(api->handle, "get_number_of_phase_pairs");
    api->get_primary_field_id_of_phase = (get_primary_field_id_of_phase_func)GetProcAddress(api->handle, "get_primary_field_id_of_phase");
    api->get_phase_id_of_fields = (get_phase_id_of_fields_func)GetProcAddress(api->handle, "get_phase_id_of_fields");
    api->get_field_ids_in_layer = (get_field_ids_in_layer_func)GetProcAddress(api->handle, "get_field_ids_in_layer");
    api->get_phase_pair_id = (get_phase_pair_id_func)GetProcAddress(api->handle, "get_phase_pair_id");
    api->get_state_variable_array = (get_state_variable_array_func)GetProcAddress(api->handle, "get_state_variable_array");
    api->get_simulation_array = (get_simulation_array_func)GetProcAddress(api->handle, "get_simulation_array");
    api->get_simulation_tracer_array = (get_simulation_tracer_array_func)GetProcAddress(api->handle, "get_simulation_tracer_array");
    api->get_simulation_quantity = (get_simulation_quantity_func)GetProcAddress(api->handle, "get_simulation_quantity");
    api->get_wall_interfaces_temperature = (get_wall_interfaces_temperature_func)GetProcAddress(api->handle, "get_wall_interfaces_temperature");
    api->get_flow_pattern = (get_flow_pattern_func)GetProcAddress(api->handle, "get_flow_pattern");
    api->get_liqliq_flow_pattern = (get_flow_pattern_func)GetProcAddress(api->handle, "get_liqliq_flow_pattern");
    api->get_plugin_input_data_table_quantity = (get_plugin_input_data_table_quantity_func)GetProcAddress(api->handle, "get_plugin_input_data_table_quantity");
    api->get_tracer_id = (get_tracer_id_func)GetProcAddress(api->handle, "get_tracer_id");
    api->get_tracer_name_size = (get_tracer_name_size_func)GetProcAddress(api->handle, "get_tracer_name_size");
    api->get_tracer_name = (get_tracer_name_func)GetProcAddress(api->handle, "get_tracer_name");
    api->get_tracer_ref_by_name = (get_tracer_ref_by_name_func)GetProcAddress(api->handle, "get_tracer_ref_by_name");
    api->get_tracer_partition_coefficient = (get_tracer_partition_coefficient_func)GetProcAddress(api->handle, "get_tracer_partition_coefficient");
    api->get_plugin_input_data_multiplereference_selected_size = (get_plugin_input_data_multiplereference_selected_size_func)GetProcAddress(api->handle, "get_plugin_input_data_multiplereference_selected_size");
    api->get_ucm_friction_factor_input_variable = (get_input_variable_func)GetProcAddress(api->handle, "get_ucm_friction_factor_input_variable");
    api->get_ucm_fluid_geometrical_properties = (get_ucm_fluid_geometrical_properties_func)GetProcAddress(api->handle, "get_ucm_fluid_geometrical_properties");
    api->get_liq_liq_flow_pattern_input_variable = (get_input_variable_func)GetProcAddress(api->handle, "get_liq_liq_flow_pattern_input_variable");
    api->get_liquid_effective_viscosity_input_variable = (get_input_variable_func)GetProcAddress(api->handle, "get_liquid_effective_viscosity_input_variable");
    api->get_gas_liq_surface_tension_input_variable = (get_input_variable_func)GetProcAddress(api->handle, "get_gas_liq_surface_tension_input_variable");
    api->get_liq_liq_shear_force_per_volume_input_variable = (get_input_variable_func)GetProcAddress(api->handle, "get_liq_liq_shear_force_per_volume_input_variable");
    api->get_relative_emulsion_viscosity = (get_relative_emulsion_viscosity_func)GetProcAddress(api->handle, "get_relative_emulsion_viscosity");

    return SDK_OK;
}

/*!
    Unload ALFAsim-SDK API dll.

    @param[in] api ALFAsim-SDK API.
    @return An #sdk_load_error_code value.
*/
inline void alfasim_sdk_close(ALFAsimSDK_API* api)
{
    FreeLibrary(api->handle);
    api->handle = nullptr;
}

#endif
