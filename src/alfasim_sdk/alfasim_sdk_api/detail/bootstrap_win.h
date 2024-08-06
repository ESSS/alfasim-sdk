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

    // https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryw
    // > If the function fails, the return value is NULL.
    api->handle = LoadLibraryW(full_filepath);
    free(executable_dir_from_env);
    if (api->handle == NULL) {
        return SDK_FAILED_TO_LOAD_DLL;
    }

    // https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress
    // > If the function fails, the return value is NULL.
    #define LOAD_SDK_PROC_MAP_TYPE(func_name, func_type) {\
        api->func_name = (func_type)GetProcAddress(api->handle, #func_name);\
        if (api->func_name == NULL) {\
            FreeLibrary(api->handle);\
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
    LOAD_SDK_PROC(get_primary_field_id_of_phase)
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
