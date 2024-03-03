import utils.functions as SelftosUtils
import json
import os
from loaders.theme_loader import theme

# TODO: Update validation rules for the config file, it's missing some rules.

class ConfigLoader:
    PREFIX = f"<[{theme.prefix}]ConfigLoader[/{theme.prefix}]>"
    CONFIG_PATH = "config/core/config.json"
    ROLES_PATH = "config/core/roles.json"
    BANS_PATH = "config/banned-users.json"
    MUTES_PATH = "config/muted-users.json"
    ADMINS_PATH = "config/ops.json"

    room_config = {}

    main_config: dict ={
        "host": "localhost", # Host to listen on
        "port": 7030, # Port to listen on
        "id": "selftos", # Server ID to be displayed in the command prompt.
        "name": "Selftos Chat Room", # Room name to be displayed in the rooms list
        "description": "A chat room for Selftos!", # Room description
        "maxUsers": 5, # Maximum number of users allowed in the room
        "private": False, # If True, the room will be hidden from the rooms list
        "owner": {
            "uid": "", # User ID
            "name": "" # User name
        },
        "show_muted_messages": True, # Prints muted user messages to the console if True
        "show_executed_commands": True, # Prints executed commands by users to the console if True
        "theme": "default" # Theme to be used in the room
    }

    roles_config = [
    {
        "name": "User",
        "level": 1,
        "color": "cyan",
        "permissions": {
        "help": ["*"],
        "list": ["users"],
        "pm": ["*"],
        "theme": ["*"]
        },
        "default": True,
    },
    {
        "name": "Admin",
        "level": 2,
        "color": "green2",
        "permissions": {
        "help": ["*"],
        "list": ["*"],
        "pm": ["*"],
        "theme": ["*"],
        "kick": ["*"],
        "ban": ["*"],
        "unban": ["*"],
        "mute": ["*"],
        "unmute": ["*"],
        "reload": ["plugins"],
        },
        "users": []
    }
    ]

    initial_configs: dict = {
        CONFIG_PATH: main_config,
        ROLES_PATH: roles_config,
        BANS_PATH: [],
        MUTES_PATH: [],
        ADMINS_PATH: []
    }

    valid_key_types: dict = {
        "host": str,
        "port": int,
        "id": str,
        "name": str,
        "description": str,
        "maxUsers": int,
        "private": bool,
        "owner": object,
        "show_muted_messages": bool,
        "show_executed_commands": bool,
        "theme": str
    }

    # Check if the config file exists
    def load_config(self):
        config_exists = os.path.exists("config")
        if not config_exists:
            SelftosUtils.printf(f"{self.PREFIX} [{theme.warning}]Warning:[/{theme.warning}] [{theme.indicator}]config[/{theme.indicator}] directory doesn't exist.")
            SelftosUtils.printf(f"{self.PREFIX} Creating [{theme.indicator}]config[/{theme.indicator}] directory...")
            try: os.mkdir("config")
            except Exception as e:
                SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] {e}")
                exit(1)
            else:
                SelftosUtils.printf(f"{self.PREFIX} [{theme.indicator}]config[/{theme.indicator}] directory created successfully.")
        core_exists = os.path.exists("config/core")
        if not core_exists:
            SelftosUtils.printf(f"{self.PREFIX} [{theme.warning}]Warning:[/{theme.warning}] [{theme.indicator}]config/core[/{theme.indicator}] directory doesn't exist.")
            SelftosUtils.printf(f"{self.PREFIX} Creating [{theme.indicator}]config/core[/{theme.indicator}] directory...")
            try: os.mkdir("config/core")
            except Exception as e:
                SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] {e}")
                exit(1)
            else:
                SelftosUtils.printf(f"{self.PREFIX} [{theme.indicator}]config/core[/{theme.indicator}] directory created successfully.")
        is_ready = True
        for file in [self.CONFIG_PATH, self.ROLES_PATH, self.BANS_PATH, self.MUTES_PATH, self.ADMINS_PATH]:
            if not os.path.exists(file):
                is_ready = False
                SelftosUtils.printf(f"{self.PREFIX} [{theme.warning}]Warning:[/{theme.warning}] [{theme.indicator}]{file}[/{theme.indicator}] doesn't exist.")
                SelftosUtils.printf(f"{self.PREFIX} Creating {file}...")
                try:
                    json.dump(self.initial_configs[file], open(file, "w"), indent=2)
                except Exception as e:
                    SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] {e}")
                    exit(1)
                SelftosUtils.printf(f"{self.PREFIX} [{theme.indicator}]{file}[/{theme.indicator}] created successfully.")
        if not is_ready:
            SelftosUtils.printf(f"{self.PREFIX} [{theme.warning}]Warning:[/{theme.warning}] Some files were missing and have been created. Please edit them and start the server.")
            exit(1)
    # Validate the core config file
    def validate_core_config(self) -> bool:
        global room_config
        try:
            room_config = json.load(open(self.CONFIG_PATH, "r"))
        except ValueError:
            SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] Invalid JSON in '{self.CONFIG_PATH}'.")
            return False
        except:
            SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] Failed to load '{self.CONFIG_PATH}'.")
            return False
        for key in self.main_config.keys():
            if key not in room_config.keys():
                SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] Option [{theme.indicator}]{key}[/{theme.indicator}] not found in '{self.CONFIG_PATH}'.")
                return False
            if not isinstance(room_config[key], self.valid_key_types[key]):
                SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] Option [{theme.indicator}]{key}[/{theme.indicator}] value type is not valid in '{self.CONFIG_PATH}'.")
                return False
        return True

    def set_roles_to_config(self) -> bool:
        room_config["roles"] = []
        room_config["default_role"] = ""
        try:
            roles = json.load(open(self.ROLES_PATH, "r"))
            for role in roles:
                if role.get("default") is True:  # Check if "default" is explicitly True
                    room_config["default_role"] = role["name"]
                room_config["roles"].append(role)
        except Exception as e:
            SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] {e}")
            return False
        return True

    def show_room_config(self, config: dict) -> None:
        if config["owner"]["name"] == "":
            config["owner"] = {
                "uid": "",
                "name": "None"
            }
        SelftosUtils.printf(f"{self.PREFIX} Host is set to [{theme.indicator}]{config['host']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} Port is set to [{theme.indicator}]{config['port']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} ID is set to [{theme.indicator}]{config['id']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} Name is set to [{theme.indicator}]{config['name']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} Description is set to [{theme.indicator}]{config['description']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} Maximum number of users is set to [{theme.indicator}]{config['maxUsers']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} Private is set to [{theme.indicator}]{config['private']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} Owner is set to [{theme.indicator}]{config['owner']['name']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} Show muted messages is set to [{theme.indicator}]{config['show_muted_messages']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} Show executed commands is set to [{theme.indicator}]{config['show_executed_commands']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} Theme is set to [{theme.indicator}]{theme.theme['general']['name']}[/{theme.indicator}].")
        SelftosUtils.printf(f"{self.PREFIX} Loading roles...")
        SelftosUtils.printf(f"{self.PREFIX} Default role is set to [{theme.indicator}]{config['default_role']}[/{theme.indicator}].")
        for role in config['roles']:
            SelftosUtils.printf(f"{self.PREFIX} [{theme.indicator}]{role['name']}[/{theme.indicator}] role is ready!")

    def load(self) -> dict:
        """
        Validates and returns the config file for server to use.
        """
        self.load_config()
        if not self.validate_core_config():
            exit(1)
        
        if not self.set_roles_to_config():
            SelftosUtils.printf(f"{self.PREFIX} [{theme.error}]Error:[/{theme.error}] Failed to load roles in '{self.ROLES_PATH}'.")
            exit(1)

        if room_config.get("owner") != None and room_config["owner"]["uid"] != "" and room_config["owner"]["name"] != "":
            with open('config/ops.json', "r") as ops_list:
                ops = json.load(ops_list)
            for op in ops:
                if op["uid"] == room_config["owner"]["uid"]:
                    break
            else:
                with open("config/ops.json", "w") as ops_list:
                    obj = {
                        "uid": room_config["owner"]["uid"],
                        "name": room_config["owner"]["name"]
                    }
                    ops.append(obj)
                    json.dump(ops, ops_list, indent=2)
                SelftosUtils.printf(f"{self.PREFIX} [{theme.indicator}]{room_config['owner']['name']}[/{theme.indicator}] has been added to the operators list.")

        self.show_room_config(room_config)
        SelftosUtils.printf(f"{self.PREFIX} Finished loading the config.")
        return room_config