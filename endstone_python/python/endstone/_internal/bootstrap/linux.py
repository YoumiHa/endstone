import ctypes.util
import os
import stat
from pathlib import Path

from endstone._internal.bootstrap.base import Bootstrap


class LinuxBootstrap(Bootstrap):
    @property
    def name(self) -> str:
        return "LinuxBootstrap"

    @property
    def target_system(self) -> str:
        return "Linux"

    @property
    def executable_filename(self) -> str:
        return "bedrock_server"

    @property
    def _endstone_runtime_filename(self) -> str:
        return "libendstone_runtime.so"

    def _download_finished(self) -> None:
        super()._download_finished()
        st = os.stat(self.executable_path)
        os.chmod(self.executable_path, st.st_mode | stat.S_IEXEC)

    def _create_process(self, *args, **kwargs) -> None:
        env = os.environ.copy()
        env["LD_PRELOAD"] = str(self._endstone_runtime_path.absolute())
        env["LD_LIBRARY_PATH"] = str(self._linked_libpython_path.parent.absolute())
        super()._create_process(env=env)

    @property
    def _linked_libpython_path(self) -> Path:
        """
        Find the path of the linked libpython on Unix systems.

        From https://gist.github.com/tkf/d980eee120611604c0b9b5fef5b8dae6

        Returns:
            (Path): Path object representing the path of the linked libpython.
        """

        class Dl_info(ctypes.Structure):
            # https://www.man7.org/linux/man-pages/man3/dladdr.3.html
            _fields_ = [
                ("dli_fname", ctypes.c_char_p),
                ("dli_fbase", ctypes.c_void_p),
                ("dli_sname", ctypes.c_char_p),
                ("dli_saddr", ctypes.c_void_p),
            ]

        libdl = ctypes.CDLL(ctypes.util.find_library("dl"))
        libdl.dladdr.argtypes = [ctypes.c_void_p, ctypes.POINTER(Dl_info)]
        libdl.dladdr.restype = ctypes.c_int

        dlinfo = Dl_info()
        retcode = libdl.dladdr(ctypes.cast(ctypes.pythonapi.Py_GetVersion, ctypes.c_void_p), ctypes.pointer(dlinfo))
        assert retcode != 0, ValueError(
            "dladdr cannot match the address of ctypes.pythonapi.Py_GetVersion to a shared object"
        )
        path = Path(dlinfo.dli_fname.decode()).resolve()
        return path
