import sys
import os
import importlib.util
import utils.functions as SelftosUtils
import library.network as SelftosNetwork

from typing import List

# TODO - Add validation for plugin class,
# TODO - Add unload method for specified plugin
# FIXED BUG - Reloading plugins cause online users to be duplicated in the room's online users list which is weird.

class PluginLoader:
    PREFIX = "<PluginLoader>"

    def __init__(self):
        self.plugin_directory = "plugins"
        self.plugins = []

    def load_plugins(self):
        sys.path.append(os.path.abspath(self.plugin_directory))

        for filename in os.listdir(self.plugin_directory):
            if filename.endswith('.pyd'):
                module_name = filename[:-4]  # Remove the '.pyd' extension
                SelftosUtils.printf(f"{self.PREFIX} Loading plugin [cyan]{filename}[/cyan]...")
                try:
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(self.plugin_directory, filename))
                    if spec is not None:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module) if spec.loader is not None else None
                        
                        plugin_class = getattr(module, module_name)
                        plugin_instance = plugin_class()
                        self.plugins.append(plugin_instance)
                except Exception as e:
                    SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] Failed to load [cyan]{filename}[/cyan]. Cause: {e}")
                    continue
                else:
                    SelftosUtils.printf(f"{self.PREFIX} Loaded [cyan]{plugin_instance.name}[/cyan] successfully!")

        if len(self.plugins) == 0:
            SelftosUtils.printf(f"{self.PREFIX} [orange1]Warning:[/orange1] No plugins were loaded!")
        else:
            SelftosUtils.printf(f"{self.PREFIX} Successfully loaded [cyan]{len(self.plugins)}[/cyan] plugins. Type [italic]list [yellow]plugins[/yellow][/italic] to see them.")

    def reload_plugins(self, online_users: List[SelftosNetwork.User]):
        SelftosUtils.printf(f"{self.PREFIX} Reloading plugins...")
        # Clear the existing plugins
        self.plugins = []
        
        # Remove the plugin directory from sys.path to ensure clean reload
        sys.path.remove(os.path.abspath(self.plugin_directory))
        
        # Load plugins again
        self.load_plugins()
        for plugin in self.plugins:
            plugin.set_online_users(online_users)
        SelftosUtils.printf(f"{self.PREFIX} Plugins reloaded successfully!")
    
    def unload_plugin(self, plugin_name: str):
        target_module_name = plugin_name.replace(" ", "")
        for plugin in self.plugins:
            module_name = plugin.name.replace(" ", "")
            if module_name == target_module_name:
                self.plugins.remove(plugin)
                SelftosUtils.printf(f"{self.PREFIX} Unloaded [cyan]{module_name}.pyd[/cyan] successfully!")
                return
        SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] Plugin [cyan]{target_module_name}.pyd[/cyan] not found!")
