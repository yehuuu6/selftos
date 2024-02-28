import json
import os
import utils.functions as SelftosUtils

class ThemeLoader:
    PREFIX = "<ThemeLoader>"
    def __init__(self):
        self.theme_path = "config/themes/"
        self.theme = self.load_theme()
        self.console = self.set_console_color()
        self.users = self.set_user_colors()
        self.plugins = self.set_plugins_color()
        self.success = self.set_success_color()
        self.warning = self.set_warning_color()
        self.error = self.set_error_color()
        self.indicator = self.set_indicator_color()

    def load_theme(self):
        try:
            for theme in os.listdir(self.theme_path):
                if theme.endswith(".json"):
                    with open(self.theme_path + theme, "r") as file:
                        return json.load(file)
        except Exception as e:
            SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] Failed to load theme. Cause: {e}")
            exit(1)

    def get_theme(self):
        if self.theme is None:
            return None
        name = self.theme["general"]["name"]
        SelftosUtils.printf(f"{self.PREFIX} Loaded theme [{self.indicator}]{name}[/{self.indicator}].")
        return self.theme
    
    def set_console_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["console"]
    
    def set_user_colors(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["users"]
    
    def set_plugins_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["plugins"]
    
    def set_success_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["success"]
    
    def set_warning_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["warning"]

    def set_error_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["error"]
    
    def set_indicator_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["indicator"]