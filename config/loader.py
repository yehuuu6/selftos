import utils.functions as SelftosUtils
import json
import os

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
    "owner": "", # Owner name. If not empty, the user will be granted admin permissions directly
    "show_muted_messages": True, # Prints muted user messages to the console if True
    "message_logging": "disabled", # Creates a log file. Values: "disabled", "messages", "console", "all"
}

roles_config = [
  {
    "name": "User",
    "level": 1,
    "permissions": {
      "list": ["users"],
      "pm": ["*"],
      "theme": ["*"]
    },
    "default": True,
  },
  {
    "name": "Admin",
    "level": 2,
    "permissions": {
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
    "owner": str,
    "show_muted_messages": bool,
    "message_logging": str
}

valid_logging_values = ["disabled", "messages", "console", "all"]

# Check if the config file exists
def load_config():
    SelftosUtils.printf(f"<CONSOLE> Loading config...")
    core_exists = os.path.exists("config/core")
    if not core_exists:
        try: os.mkdir("config/core")
        except Exception as e:
            SelftosUtils.printf(f"<CONSOLE> [red]Error:[/red] {e}")
            exit(1)
    is_ready = True
    for file in [CONFIG_PATH, ROLES_PATH, BANS_PATH, MUTES_PATH, ADMINS_PATH]:
        if not os.path.exists(file):
            is_ready = False
            SelftosUtils.printf(f"<CONSOLE> [orange1]Warning:[/orange1] [bold yellow]{file}[/bold yellow] doesn't exist.")
            SelftosUtils.printf(f"<CONSOLE> Creating {file}...")
            try:
                json.dump(initial_configs[file], open(file, "w"), indent=2)
            except Exception as e:
                SelftosUtils.printf(f"<CONSOLE> [red]Error:[/red] {e}")
                exit(1)
            SelftosUtils.printf(f"<CONSOLE> [bold yellow]{file}[/bold yellow] created successfully.")
    if not is_ready:
        SelftosUtils.printf(f"<CONSOLE> Some files were missing and have been created. Please edit them and boot the server.")
        exit(1)

# Validate the core config file
def validate_core_config() -> bool:
    global room_config
    try:
        room_config = json.load(open(CONFIG_PATH, "r"))
    except ValueError:
        SelftosUtils.printf(f"<CONSOLE> [red]Error:[/red] Invalid JSON in '{CONFIG_PATH}'.")
        return False
    for key in main_config.keys():
        if key not in room_config.keys():
            SelftosUtils.printf(f"<CONSOLE> [red]Error:[/red] Option [bold yellow]{key}[/bold yellow] not found in '{CONFIG_PATH}'.")
            return False
        if not isinstance(room_config[key], valid_key_types[key]):
            SelftosUtils.printf(f"<CONSOLE> [red]Error:[/red] Option [bold yellow]{key}[/bold yellow] value type is not valid in '{CONFIG_PATH}'.")
            return False
        if key == "message_logging" and room_config[key] not in valid_logging_values:
            SelftosUtils.printf(f"<CONSOLE> [red]Error:[/red] Option [bold italic yellow]{key}[/bold italic yellow] doesn't have a valid value ('{room_config[key]}') in '{CONFIG_PATH}'.")
            return False
    return True

def set_roles_to_config() -> bool:
    room_config["roles"] = []
    room_config["default_role"] = ""
    try:
        roles = json.load(open(ROLES_PATH, "r"))
        for role in roles:
            if role.get("default") is True:  # Check if "default" is explicitly True
                room_config["default_role"] = role["name"]
            room_config["roles"].append(role)
    except Exception as e:
        return False
    return True


def load() -> dict:
    """
    Validates and returns the config file for server to use.
    """
    load_config()
    if not validate_core_config():
        exit(1)
    
    if not set_roles_to_config():
        SelftosUtils.printf(f"<CONSOLE> [red]Error:[/red] Failed to load roles in '{ROLES_PATH}'.")
        exit(1)

    SelftosUtils.printf(f"<CONSOLE> Config loaded [bold green]successfully[/bold green].")
    SelftosUtils.show_room_config(room_config)
    return room_config

config = load()