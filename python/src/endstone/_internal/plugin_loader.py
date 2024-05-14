import glob
import importlib.util
import os.path
import site
import subprocess
import sys
from pathlib import Path
from importlib.metadata import entry_points, metadata
from typing import List
from endstone import Server
from endstone.command import Command
from endstone.permissions import Permission, PermissionDefault
from endstone.plugin import PluginDescription, PluginLoader, Plugin, PluginLoadOrder

__all__ = ["PythonPluginLoader"]


def find_python():
    if sys.platform != "win32":
        return sys.executable

    for path in sys.path:
        assumed_path = os.path.join(path, "python.exe")
        if os.path.isfile(assumed_path):
            return assumed_path

    raise Exception("Python executable not found")


class PythonPluginLoader(PluginLoader):
    SUPPORTED_API = ["0.2", "0.3", "0.4"]

    def __init__(self, server: Server):
        PluginLoader.__init__(self, server)
        self._plugins = []

    @staticmethod
    def _build_commands(commands: dict) -> list[Command]:
        results = []
        for name, command in commands.items():
            command = Command(name, **command)
            results.append(command)
        return results

    @staticmethod
    def _build_permissions(permissions: dict) -> list[Permission]:
        results = []
        for name, permission in permissions.items():
            if "default" in permission:
                value = permission["default"]
                if isinstance(value, bool):
                    permission["default"] = PermissionDefault.TRUE if value else PermissionDefault.FALSE
                elif isinstance(value, str):
                    permission["default"] = PermissionDefault.__members__[value.strip().replace(" ", "_").upper()]
                elif not isinstance(value, PermissionDefault):
                    raise TypeError(f"Invalid value for default permission: {value}")

            permission = Permission(name, **permission)
            results.append(permission)
        return results

    @staticmethod
    def _load_module(module_name: str, path: str) -> None:
        path = Path(path)
        module_parts = module_name.split(".")
        spec = None

        # Check for package
        package_location = path.joinpath(*module_parts, "__init__.py")
        if package_location.exists():
            spec = importlib.util.spec_from_file_location(module_name, package_location)

        # Check for module file
        module_file = module_parts.pop() + ".py"
        module_location = path.joinpath(*module_parts, module_file)
        if module_location.exists():
            spec = importlib.util.spec_from_file_location(module_name, module_location)

        if spec is None:
            raise ModuleNotFoundError(module_name)

        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

    def load_plugins(self, directory) -> List[Plugin]:
        env = os.environ.copy()
        env.pop("LD_PRELOAD", "")

        for file in glob.glob(os.path.join(directory, "*.whl")):
            subprocess.run(
                [
                    find_python(),
                    "-m",
                    "pip",
                    "install",
                    file,
                    "--user",
                    "--quiet",
                    "--no-warn-script-location",
                ],
                env=env,
            )

        loaded_plugins = []
        eps = entry_points(group="endstone")
        for ep in eps:
            # get distribution metadata, use as fallback for name and version
            ep_name = ep.name.replace("-", "_")
            dist_name = "endstone_" + ep_name
            plugin_metadata = metadata(dist_name).json

            # load module
            try:
                cls = ep.load()
            except ModuleNotFoundError:
                self._load_module(ep.module, site.USER_SITE)
                cls = ep.load()

            # prepare plugin description
            cls_attr = dict(cls.__dict__)
            name = cls_attr.pop("name", ep_name.replace("_", " ").title().replace(" ", ""))
            version = cls_attr.pop("version", plugin_metadata["version"])

            api_version = cls_attr.pop("api_version", None)
            if api_version is None:
                self.server.logger.warning(
                    f"Plugin '{name}' does not specify an API version. This may prevent the plugin from loading in "
                    f"future releases."
                )
            elif api_version not in self.SUPPORTED_API:
                self.server.logger.error(
                    f"Error occurred when trying to load plugin '{name}': plugin was designed for API version: "
                    f"{api_version} which is not compatible with this server."
                )
                continue

            load = cls_attr.pop("load", None)
            if load is not None:
                if isinstance(load, str):
                    load = PluginLoadOrder.__members__[load.strip().replace(" ", "_").upper()]
                elif not isinstance(load, PluginLoadOrder):
                    raise TypeError(f"Invalid value for load order: {load}")

            commands = cls_attr.pop("commands", {})
            commands = self._build_commands(commands)

            permissions = cls_attr.pop("permissions", {})
            permissions = self._build_permissions(permissions)

            plugin_description = PluginDescription(
                name=name, version=version, load=load, commands=commands, permissions=permissions, **cls_attr
            )

            # instantiate plugin
            plugin = cls()
            if not isinstance(plugin, Plugin):
                raise TypeError(f"Main class {ep.value} does not extend endstone.plugin.Plugin")
            plugin._description = plugin_description
            self._plugins.append(plugin)
            loaded_plugins.append(plugin)

        return loaded_plugins
