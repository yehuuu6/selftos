from typing import List

import json
import os
import utils.functions as SelftosUtils

default_theme: dict = {
    "general": {
        "name": "Default",
        "description": "Default theme for the Selftos chat server.",
        "author": "yehuuu6"
    },
    "colors": {
        "prefix": "magenta",
        "users": "cyan",
        "plugins": "blue",
        "error": "red",
        "success": "green3",
        "warning": "orange1",
        "indicator": "bold yellow"
    }
}

class ThemeLoader:
    PREFIX = "<ThemeLoader>"
    def __init__(self):
        self.__theme_path = "config/themes/"
        self.theme = self.__set_theme()
        self.prefix = self.__set_prefix_color()
        self.users = self.__set_user_colors()
        self.plugins = self.__set_plugins_color()
        self.success = self.__set_success_color()
        self.warning = self.__set_warning_color()
        self.error = self.__set_error_color()
        self.indicator = self.__set_indicator_color()
        self.__override_default_theme()

    def __validate_theme(self, theme: dict, name) -> bool:
        required_properties = ["general", "colors"]
        required_sub_properties_general = ["name", "description", "author"]
        required_sub_properties_colors = ["prefix", "users", "plugins", "error", "success", "warning", "indicator"]
        
        # Check properties
        for prop in required_properties:
            if prop not in theme:
                SelftosUtils.printf(f"{self.PREFIX} [orange1]Warning:[/orange1] Missing required property '{prop}' in theme. Skipping '{name.capitalize()}'.")
                return False
        # Check sub-properties
        for prop in required_sub_properties_general:
            if prop not in theme["general"]:
                SelftosUtils.printf(f"{self.PREFIX} [orange1]Warning:[/orange1] Missing required property '{prop}' in theme.general. Skipping '{name.capitalize()}'.")
                return False
        for prop in required_sub_properties_colors:
            if prop not in theme["colors"]:
                SelftosUtils.printf(f"{self.PREFIX} [orange1]Warning:[/orange1] Missing required property '{prop}' in theme.colors. Skipping '{name.capitalize()}'.")
                return False
        return True

    def __override_default_theme(self):
        # Save the default theme to the system every time the theme is loaded
        try:
            with open(self.__theme_path + "default.json", "w") as file:
                json.dump(default_theme, file, indent=2)
        except Exception as e:
            SelftosUtils.printf(f"{self.PREFIX} [orange1]Warning:[/orange1] Failed to save default theme to system. Cause: {e}")

    def __load_themes(self):
        # Load all themes from the system and return a list of themes
        themes: List[dict] = []
        try:
            for theme in os.listdir(self.__theme_path):
                if theme.endswith(".json"):
                    with open(self.__theme_path + theme, "r") as file:
                        file_name = theme[:-5]
                        t = json.load(file)
                        if self.__validate_theme(t, file_name):
                            themes.append(t)
            return themes
        except Exception as e:
            SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] Failed to load themes. Cause: {e}")
            exit(1)

    def __set_theme(self) -> dict:
        # Check if config/themes directory exists
        try:
            if not os.path.exists("config/themes"):
                os.mkdir("config/themes")
        except Exception as e:
            SelftosUtils.printf(f"{self.PREFIX} [orange1]Warning:[/orange1] Failed to create themes directory. Cause: {e}")
            return default_theme

        # Read config file and set the theme
        themes = self.__load_themes()
        try:
            with open("config/core/config.json", "r") as file:
                config = json.load(file)
                theme = config["theme"]
        except Exception as e:
            SelftosUtils.printf(f"{self.PREFIX} [orange1]Warning:[/orange1] Failed to read config file. Cause: {e}")
            # Use default theme if failed to read config file
            return default_theme
        for t in themes:
            if (t["general"]["name"]).lower() == theme:
                return t
        else:
            if theme != "default":
                SelftosUtils.printf(f"{self.PREFIX} [orange1]Warning:[/orange1] Theme '{theme.capitalize()}' not found. Using default theme instead.")
            else:
                SelftosUtils.printf(f"{self.PREFIX} [orange1]Warning:[/orange1] Theme 'default' not found. Creating a new one.")
            return default_theme
    
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