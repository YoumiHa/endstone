#ifdef _WIN32

#include "endstone/common.h"
#include "hook/hook_manager.h"
#include "pybind/pybind.h"

#include <Windows.h>

std::unique_ptr<py::scoped_interpreter> g_interpreter;
std::unique_ptr<py::gil_scoped_release> g_release;

BOOL WINAPI DllMain(_In_ HINSTANCE,          // handle to DLL module
                    _In_ DWORD fdwReason,    // reason for calling function
                    _In_ LPVOID lpvReserved) // reserved
{
    // Perform actions based on the reason for calling.
    switch (fdwReason) {
    case DLL_PROCESS_ATTACH: {
        try {
            // Initialize python interpreter and release the GIL
            g_interpreter = std::make_unique<py::scoped_interpreter>();
            py::module_::import("threading"); // https://github.com/pybind/pybind11/issues/2197
            g_release = std::make_unique<py::gil_scoped_release>();

            // Initialize hook manager
            HookManager::initialize();
            break;
        }
        catch (const std::exception &e) {
            printf("LibEndstone loads failed.\n");
            if (const auto *se = dynamic_cast<const std::system_error *>(&e)) {
                printf("%s, error code: %d.\n", se->what(), se->code().value());
            }
            else {
                printf("%s\n", e.what());
            }
            return FALSE; // Return FALSE to fail DLL load.
        }
    }
    case DLL_PROCESS_DETACH: {
        if (lpvReserved != nullptr) {
            break; // do not do cleanup if process termination scenario
        }

        // Perform any necessary cleanup.
        HookManager::finalize();
        g_release.reset();
        g_interpreter.reset();

        break;
    }
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    default:
        // Do thread-specific initialization or cleanup.
        break;
    }

    return TRUE; // Successful DLL_PROCESS_ATTACH.
}

#endif // _WIN32