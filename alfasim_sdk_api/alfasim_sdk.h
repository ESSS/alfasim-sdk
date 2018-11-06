#include <alfasim_sdk_api/detail/api_pointers.h>
#if defined(_WIN32)
#include <alfasim_sdk_api/detail/bootstrap_win.h>
#elif defined(UNIX)
#include <alfasim_sdk_api/detail/bootstrap_linux.h>
#endif