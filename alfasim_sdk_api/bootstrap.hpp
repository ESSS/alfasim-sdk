#include <iostream>
#include <string>
#include <windows.h>
#include <stdlib.h>

struct alfasim_sdk_bootstrap {
    alfasim_sdk_bootstrap()
    {
        #if defined(WIN32)
        auto DLL_FILENAME = L"/alfasim_plugins_api-MD.dll";

        WCHAR path[MAX_PATH];
        GetModuleFileNameW(NULL, path, MAX_PATH);
        auto pos = std::wstring(path).find_last_of(L"\\/");
        auto current_exe = std::wstring(path).substr(0, pos);
        std::wstring ALFASIM_PATH(current_exe);
        WCHAR *ENV_ALFASIM_PATH = _wgetenv(L"ALFASIM_PATH");
        if (ENV_ALFASIM_PATH != NULL) {
            ALFASIM_PATH = ENV_ALFASIM_PATH;
        }
        std::wstring FULL_PATH = ALFASIM_PATH + DLL_FILENAME;

        this->dllHandle = LoadLibrary(FULL_PATH.c_str());
        if (dllHandle == NULL) {
            std::cout << "Couldn't load dll file." << std::endl;
            return;
        }

        get_test_number = (get_test_number_func)GetProcAddress(dllHandle, "get_test_number");
        get_plugin_input_data_int = (get_plugin_input_data_int_func)GetProcAddress(dllHandle, "get_plugin_input_data_int");
        #elif defined(UNIX)
        #endif
    }

    ~alfasim_sdk_bootstrap()
    {
        FreeLibrary(this->dllHandle);
    }

    HINSTANCE dllHandle = NULL;
};
alfasim_sdk_bootstrap _;