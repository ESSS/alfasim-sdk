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
        get_plugin_variable = (get_plugin_variable_func)dlsym(this->m_handle, "get_plugin_variable");
    }

    ~alfasim_sdk_bootstrap()
    {
        dlclose(this->m_handle);
    }

    void* m_handle;
};
alfasim_sdk_bootstrap _;

#endif
