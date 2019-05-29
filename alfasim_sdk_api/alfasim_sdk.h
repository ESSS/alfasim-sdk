#include <alfasim_sdk_api/common.h>
#include <alfasim_sdk_api/detail/api_pointers.h>
#if defined(_WIN32)
#include <alfasim_sdk_api/detail/bootstrap_win.h>
#elif defined(unix) || defined(__unix__) || defined(__unix)
#include <alfasim_sdk_api/detail/bootstrap_linux.h>
#else
#error "Unknown host (Alfasim SDK will only work on Linux and Windows)"
#endif
