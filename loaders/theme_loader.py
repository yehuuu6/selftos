import json
import os
import utils.functions as SelftosUtils

class ThemeLoader:
    PREFIX = "<ThemeLoader>"
    def __init__(self):
        self.theme_path = "config/themes/"
        self.theme = self.__load_theme()
        self.prefix = self.__set_prefix_color()
        self.users = self.__set_user_colors()
        self.plugins = self.__set_plugins_color()
        self.success = self.__set_success_color()
        self.warning = self.__set_warning_color()
        self.error = self.__set_error_color()
        self.indicator = self.__set_indicator_color()

    def __load_theme(self):
        try:
            for theme in os.listdir(self.theme_path):
                if theme.endswith(".json"):
                    with open(self.theme_path + theme, "r") as file:
                        return json.load(file)
        except Exception as e:
            SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] Failed to load theme. Cause: {e}")
            exit(1)
    
    def __set_prefix_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["prefix"]
    
    def __set_user_colors(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["users"]
    
    def __set_plugins_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["plugins"]
    
    def __set_success_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["success"]
    
    def __set_warning_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["warning"]

    def __set_error_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["error"]
    
    def __set_indicator_color(self):
        if self.theme is None:
            return None
        return self.theme["colors"]["indicator"]

theme = ThemeLoader()