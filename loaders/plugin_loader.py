import sys
import os
import importlib.util
import utils.functions as SelftosUtils
import library.network as SelftosNetwork

from typing import List
from loaders.theme_loader import theme

DEBUG_MODE = True # Set to True to load .py files instead of .pyd files for hot-reloading

file_extension = ".py" if DEBUG_MODE else ".pyd"

class PluginLoader:
    PREFIX = f"<[{theme.prefix}]PluginLoader[/{theme.prefix}]>"

    def __init__(self):
        self.plugin_directory = "plugins"
        self.plugins = []

    def validate_plugin(self, plugin_instance, module_name: str) -> bool:
        required_properties = ["name", "version", "description", "author", "prefix", "online_users",
                                "on_package_received", "on_message_received", "on_user_joined", "on_user_left", "on_command_executed"]
        # Check properties
        for prop in required_properties:
            if not hasattr(plugin_instance, prop):
                SelftosUtils.printf(f"{self.PREFIX} [{theme.warning}]Warning:[/{theme.warning}] Missing required property [yellow]{prop}[/yellow] in [{theme.plugins}]{module_name}[/{theme.plugins}].")
                return False
        # Check if properties are callable
        for prop in required_properties[6:]:
            if not callable(getattr(plugin_instance, prop)):
                SelftosUtils.printf(f"{self.PREFIX} [{theme.warning}]Warning:[/{theme.warning}] Property [yellow]{prop}[/yellow] in [{theme.plugins}]{module_name}[/{theme.plugins}] is not callable.")
                return False
        return True


    def load_plugins(self) -> None:
        if not os.path.exists(self.plugin_directory):
            os.mkdir(self.plugin_directory)
            SelftosUtils.printf(f"{self.PREFIX} [{theme.warning}]Warning:[/{theme.warning}] No plugin directory found. Created a new one.")
            return
        
        sys.path.append(os.path.abspath(self.plugin_directory))

        for filename in os.listdir(self.plugin_directory):
            if filename.endswith(file_extension):
                module_name = filename[:-len(file_extension)]
                try:
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(self.plugin_directory, filename))
                    if spec is not None:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module) if spec.loader is not None else None
                        
                        plugin_class = getattr(module, module_name)
                        plugin_instance = plugin_class()
                        if not self.validate_plugin(plugin_instance, module_name):
                            SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] Plugin [{theme.plugins}]{filename}[/{theme.plugins}] is not a valid plugin!")
                            continue
                        self.plugins.append(plugin_instance)
                except Exception as e:
                    SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] Failed to load [{theme.plugins}]{filename}[/{theme.plugins}]. Cause: {e}")
                    continue
                else:
                    SelftosUtils.printf(f"{self.PREFIX} Loaded [{theme.plugins}]{plugin_instance.name}[/{theme.plugins}] successfully.")

        if len(self.plugins) == 0:
            SelftosUtils.printf(f"{self.PREFIX} No plugins were loaded.")
        else:
            SelftosUtils.printf(f"{self.PREFIX} [{theme.plugins}]{len(self.plugins)}[/{theme.plugins}] plugins are loaded and active. Type [italic]list [yellow]plugins[/yellow][/italic] to see them.")

    def reload_plugins(self, online_users: List[SelftosNetwork.User]) -> bool:
        SelftosUtils.printf(f"{self.PREFIX} [{theme.warning}]Warning:[/{theme.warning}] You may still require to restart the server to apply changes to the plugins.")
        SelftosUtils.printf(f"{self.PREFIX} Reloading plugins...")
        try:
            # Clear the existing plugins
            self.plugins = []
            
            # Remove the plugin directory from sys.path to ensure clean reload
            sys.path.remove(os.path.abspath(self.plugin_directory))
            
            # Load plugins again
            self.load_plugins()
        except Exception as e:
            SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] Failed to reload plugins. Cause: {e}")
            return False
        for plugin in self.plugins:
            plugin.online_users = online_users
        SelftosUtils.printf(f"{self.PREFIX} Plugins reloaded successfully.")
        return True
    
    def unload_plugin(self, plugin_name: str) -> bool:
        SelftosUtils.printf(f"{self.PREFIX} [{theme.warning}]Warning:[/{theme.warning}] You may still require to remove the plugin from the plugin directory to completely unload it.")
        try:
            target_module_name = plugin_name.replace(" ", "")
            for plugin in self.plugins:
                module_name = plugin.name.replace(" ", "")
                if module_name == target_module_name:
                    self.plugins.remove(plugin)
                    SelftosUtils.printf(f"{self.PREFIX} Unloaded [{theme.plugins}]{module_name}.pyd[/{theme.plugins}] successfully.")
                    return True
        except Exception as e:
            SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] Failed to unload plugin. Cause: {e}")
            return False
        SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] Plugin [{theme.plugins}]{target_module_name}[/{theme.plugins}] not found.")
        return False
