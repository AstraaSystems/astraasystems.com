import os
import importlib
import threading
from types import ModuleType

from ardhanarishvara.execution.observer import observer


# =========================================================
# Plugin Base Class
# =========================================================

class ARKAPlugin:
    """
    Base class for all ARKA plugins.

    Plugins may implement:
    - register_commands(arka)
    - register_sectors(arka)
    - register_engines(arka)
    - on_load()
    - on_unload()
    """

    name = "UnnamedPlugin"
    version = "0.0.1"

    def register_commands(self, arka):
        pass

    def register_sectors(self, arka):
        pass

    def register_engines(self, arka):
        pass

    def on_load(self):
        pass

    def on_unload(self):
        pass


# =========================================================
# Plugin Manager
# =========================================================

class PluginManager:
    """
    Loads, unloads, and manages ARKA plugins.

    Features:
    - dynamic module loading
    - plugin registry
    - hot reload
    - ARKA integration
    """

    def __init__(self, arka, plugin_dir="ardhanarishvara/plugins"):
        self.arka = arka
        self.plugin_dir = plugin_dir
        self.plugins = {}          # name -> plugin instance
        self.modules = {}          # name -> module
        self.lock = threading.Lock()

    # -----------------------------------------------------
    # Discover Plugins
    # -----------------------------------------------------
    def discover(self):
        """
        Finds all Python files in the plugin directory.
        """
        files = []
        for f in os.listdir(self.plugin_dir):
            if f.endswith(".py") and f not in ["plugin_system.py", "__init__.py"]:
                files.append(f[:-3])
        return files

    # -----------------------------------------------------
    # Load Plugin
    # -----------------------------------------------------
    def load(self, plugin_name):
        with self.lock:
            if plugin_name in self.plugins:
                raise RuntimeError(f"Plugin '{plugin_name}' already loaded")

            module_path = f"ardhanarishvara.plugins.{plugin_name}"
            module = importlib.import_module(module_path)

            # Find plugin class
            plugin_class = None
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, ARKAPlugin) and obj is not ARKAPlugin:
                    plugin_class = obj
                    break

            if not plugin_class:
                raise RuntimeError(f"No ARKAPlugin subclass found in {plugin_name}")

            plugin = plugin_class()

            # Register plugin components
            plugin.register_commands(self.arka)
            plugin.register_sectors(self.arka)
            plugin.register_engines(self.arka)

            plugin.on_load()

            self.plugins[plugin_name] = plugin
            self.modules[plugin_name] = module

            observer.emit("plugin_loaded", {"plugin": plugin_name})

    # -----------------------------------------------------
    # Unload Plugin
    # -----------------------------------------------------
    def unload(self, plugin_name):
        with self.lock:
            if plugin_name not in self.plugins:
                raise RuntimeError(f"Plugin '{plugin_name}' not loaded")

            plugin = self.plugins[plugin_name]
            plugin.on_unload()

            del self.plugins[plugin_name]
            del self.modules[plugin_name]

            observer.emit("plugin_unloaded", {"plugin": plugin_name})

    # -----------------------------------------------------
    # Reload Plugin
    # -----------------------------------------------------
    def reload(self, plugin_name):
        with self.lock:
            if plugin_name not in self.plugins:
                return self.load(plugin_name)

            # Unload
            self.unload(plugin_name)

            # Reload module
            module_path = f"ardhanarishvara.plugins.{plugin_name}"
            importlib.reload(importlib.import_module(module_path))

            # Load again
            self.load(plugin_name)

            observer.emit("plugin_reloaded", {"plugin": plugin_name})

    # -----------------------------------------------------
    # List Plugins
    # -----------------------------------------------------
    def list_plugins(self):
        return list(self.plugins.keys())
