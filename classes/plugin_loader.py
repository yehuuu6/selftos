import sys
import os
import importlib.util
import utils.functions as SelftosUtils

# TODO - Add validation for plugin class

class PluginLoader:
    def __init__(self, plugin_directory="plugins"):
        self.plugin_directory = plugin_directory
        self.plugins = []

    def load_plugins(self):
        sys.path.append(os.path.abspath(self.plugin_directory))

        for filename in os.listdir(self.plugin_directory):
            if filename.endswith('.pyd'):
                module_name = filename[:-4]  # Remove the '.pyd' extension
                SelftosUtils.printf(f"<CONSOLE> Loading plugin [cyan]{module_name}[/cyan]...")
                try:
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(self.plugin_directory, filename))
                    if spec is not None:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module) if spec.loader is not None else None
                        
                        plugin_class = getattr(module, module_name)
                        plugin_instance = plugin_class()
                        self.plugins.append(plugin_instance)
                except Exception as e:
                    SelftosUtils.printf(f"<CONSOLE> [red]Error: Failed to load plugin [cyan]{module_name}[/cyan]! Message: {e}[/red]")
                    continue
                else:
                    SelftosUtils.printf(f"<CONSOLE> Plugin [cyan]{plugin_instance.name}[/cyan] loaded [green3]successfully[/green3]!")