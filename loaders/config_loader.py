import utils.functions as SelftosUtils
import json
import os

class ConfigLoader:
    PREFIX = "<ConfigLoader>"
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
        "show_muted_messages": True, # Prints muted user messages to the ConfigLoader if True
        "show_executed_commands": True, # Prints executed commands by users to the ConfigLoader if True
        "message_logging": "disabled", # Creates a log file. Values: "disabled", "messages", "ConfigLoader", "all"
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
        "color": "red3",
        "permissions": {
        "help": ["*"],
        "list": ["*"],
        "pm": ["*"],
        "theme": ["*"],
        "kick": ["*"],
        "ban": ["*"],
        "unban": ["*"],
        "mute": ["*"],
        "unmute": ["*"]
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
        "message_logging": str
    }

    valid_logging_values = ["disabled", "messages", "ConfigLoader", "all"]

    # Check if the config file exists
    def load_config(self):
        core_exists = os.path.exists("config/core")
        if not core_exists:
            try: os.mkdir("config/core")
            except Exception as e:
                SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] {e}")
                exit(1)
        is_ready = True
        for file in [self.CONFIG_PATH, self.ROLES_PATH, self.BANS_PATH, self.MUTES_PATH, self.ADMINS_PATH]:
            if not os.path.exists(file):
                is_ready = False
                SelftosUtils.printf(f"{self.PREFIX} [orange1]Warning:[/orange1] [yellow]{file}[/yellow] doesn't exist.")
                SelftosUtils.printf(f"{self.PREFIX} Creating {file}...")
                try:
                    json.dump(self.initial_configs[file], open(file, "w"), indent=2)
                except Exception as e:
                    SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] {e}")
                    exit(1)
                SelftosUtils.printf(f"{self.PREFIX} [yellow]{file}[/yellow] created successfully.")
        if not is_ready:
            SelftosUtils.printf(f"{self.PREFIX} Some files were missing and have been created. Please edit them and boot the server.")
            exit(1)

    # Validate the core config file
    def validate_core_config(self) -> bool:
        global room_config
        try:
            room_config = json.load(open(self.CONFIG_PATH, "r"))
        except ValueError:
            SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] Invalid JSON in '{self.CONFIG_PATH}'.")
            return False
        for key in self.main_config.keys():
            if key not in room_config.keys():
                SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] Option [yellow]{key}[/yellow] not found in '{self.CONFIG_PATH}'.")
                return False
            if not isinstance(room_config[key], self.valid_key_types[key]):
                SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] Option [yellow]{key}[/yellow] value type is not valid in '{self.CONFIG_PATH}'.")
                return False
            if key == "message_logging" and room_config[key] not in self.valid_logging_values:
                SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] Option [bold italic yellow]{key}[/bold italic yellow] doesn't have a valid value ('{room_config[key]}') in '{self.CONFIG_PATH}'.")
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
            return False
        return True

    def show_room_config(self, config: dict) -> None:
        SelftosUtils.printf(f"{self.PREFIX} Host is set to [bold yellow]{config['host']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} Port is set to [bold yellow]{config['port']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} ID is set to [bold yellow]{config['id']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} Name is set to [bold yellow]{config['name']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} Description is set to [bold yellow]{config['description']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} Maximum number of users is set to [bold yellow]{config['maxUsers']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} Private is set to [bold yellow]{config['private']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} Owner is set to [bold yellow]{config['owner']['name']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} Show muted messages is set to [bold yellow]{config['show_muted_messages']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} Show executed commands is set to [bold yellow]{config['show_executed_commands']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} Message logging is set to [bold yellow]{config['message_logging']}[/bold yellow].")
        SelftosUtils.printf(f"{self.PREFIX} Loading roles...")
        SelftosUtils.printf(f"{self.PREFIX} Default role is set to [bold yellow]{config['default_role']}[/bold yellow].")
        for role in config['roles']:
            SelftosUtils.printf(f"{self.PREFIX} [bold yellow]{role['name']}[/bold yellow] role is ready!")

    def load(self) -> dict:
        """
        Validates and returns the config file for server to use.
        """
        self.load_config()
        if not self.validate_core_config():
            exit(1)
        
        if not self.set_roles_to_config():
            SelftosUtils.printf(f"{self.PREFIX} [red]Error:[/red] Failed to load roles in '{self.ROLES_PATH}'.")
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
                SelftosUtils.printf(f"{self.PREFIX} [yellow]{room_config['owner']['name']}[/yellow] has been added to the operators list.")

        self.show_room_config(room_config)
        SelftosUtils.printf(f"{self.PREFIX} Config loaded successfully.")
        return room_config