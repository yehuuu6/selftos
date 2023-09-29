import utils.functions as SelftosUtils
import json

from rich.console import Console

console = Console()

CONFIG_PATH = "config/selftos.config.json"

example_config: dict ={
    "host": "localhost", # Host to listen on
    "port": 7030, # Port to listen on
    "id": "selftos", # Server ID to be displayed in the command prompt.
    "name": "Selftos Chat Room", # Room name to be displayed in the rooms list
    "description": "A chat room for Selftos!", # Room description
    "maxUsers": 5, # Maximum number of users allowed in the room
    "private": False, # If True, the room will be hidden from the rooms list
    "owner": None, # Owner name. If not None, the owner will be added to the admins list
    "show_muted_messages": True, # Prints muted user messages to the console if True
    "message_logging": "disabled", # Creates a log file. Values: "disabled", "messages", "console", "all"
}

def validate_config(config: dict) -> bool:
    """
    If keys and values are not the same with the example config, return False
    """
    valid_options = example_config.keys()
    for key in config.keys():
        if key not in valid_options:
            SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid option [bold yellow]'{key}'[/bold yellow] in the config file.[/red]")
            SelftosUtils.printf(f"<CONSOLE> Please see the documentation at https://selftos.app/docs for setting up the config file.")
            return False
    
    # Check if we are missing any options
    for key in valid_options:
        if key not in config.keys():
            SelftosUtils.printf(f"<CONSOLE> [red]Error: Missing option [bold yellow]'{key}'[/bold yellow] in the config file.[/red]")
            SelftosUtils.printf(f"<CONSOLE> Please see the documentation at https://selftos.app/docs for setting up the config file.")
            return False
    
    valid_logging_options: dict = {
        "disabled": "Nothing will be logged.",
        "messages": "Only messages will be logged.",
        "console": "Only console output will be logged.",
        "all": "Both messages and console output will be logged."
    }
    
    if type(config['host']) is not str:
        SelftosUtils.printf(type(config['host']))
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid value for [bold yellow]'host'[/bold yellow] in the config file.[/red]")
        SelftosUtils.printf(f"- [bold yellow]'host'[/bold yellow] value must be a string.")
        return False
    elif type(config['port']) is not int:
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid value for [bold yellow]'port'[/bold yellow] in the config file.[/red]")
        SelftosUtils.printf(f"- [bold yellow]'port'[/bold yellow] value must be an integer.")
    elif type(config['id']) is not str or (len(config['id']) > 16 or len(config['id']) < 1):
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid value for [bold yellow]'id'[/bold yellow] in the config file.[/red]")
        SelftosUtils.printf(f"- [bold yellow]'id'[/bold yellow] value must be a string with a length between 1 and 16.")
        return False
    elif type(config['name']) is not str or (len(config['name']) > 42 or len(config['name']) < 5):
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid value for [bold yellow]'name'[/bold yellow] in the config file.[/red]")
        SelftosUtils.printf(f"- [bold yellow]'name'[/bold yellow] value must be a string with a length between 5 and 42.")
        return False
    elif type(config['description']) is not str or (len(config['description']) > 64 or len(config['description']) < 12):
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid value for [bold yellow]'description'[/bold yellow] in the config file.[/red]")
        SelftosUtils.printf(f"- [bold yellow]'description'[/bold yellow] value must be a string with a length between 12 and 64.")
        return False
    elif type(config['maxUsers']) is not int:
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid value for [bold yellow]'maxUsers'[/bold yellow] in the config file.[/red]")
        SelftosUtils.printf(f"- [bold yellow]'maxUsers'[/bold yellow] value must be an integer.")
        return False
    elif type(config['private']) is not bool:
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid value for [bold yellow]'private'[/bold yellow] in the config file.[/red]")
        SelftosUtils.printf(f"- [bold yellow]'private'[/bold yellow] value must be a boolean.")
        return False
    elif type(config['owner']) is not str and config['owner'] is not None:
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid value for [bold yellow]'owner'[/bold yellow] in the config file.[/red]")
        SelftosUtils.printf(f"- [bold yellow]'owner'[/bold yellow] value must be a string.")
        return False
    elif type(config['show_muted_messages']) is not bool:
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid value for [bold yellow]'show_muted_messages'[/bold yellow] in the config file.[/red]")
        SelftosUtils.printf(f"- [bold yellow]'show_muted_messages'[/bold yellow] value must be a boolean.")
        return False
    elif type(config['message_logging']) is not str or config['message_logging'] not in valid_logging_options:
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Invalid value for [bold yellow]'message_logging'[/bold yellow] in the config file.[/red]")
        SelftosUtils.printf(f"- [bold yellow]'message_logging'[/bold yellow] value must be one of the following strings:")
        for key, value in valid_logging_options.items():
            SelftosUtils.printf(f"- [bold yellow]{key}[/bold yellow]: {value}")
        return False
        
    return True
    
try:
    SelftosUtils.printf(f"<CONSOLE> Loading config file at {CONFIG_PATH}...")
    with open(CONFIG_PATH) as config_file:
        room_config: dict = json.load(config_file)
        if not validate_config(room_config):
            exit(1)
        if room_config['owner'] is not None:
            # Read the existing content of the file
            existing_owners = []
            with open("config/admins.txt", "r") as owners_file:
                existing_owners = owners_file.read().splitlines()

            # Check if the owner name is not in the existing owners list
            if room_config['owner'] not in existing_owners:
                # Append the new owner name to the file
                with open("config/admins.txt", "a") as owners_file:
                    owners_file.write(room_config['owner'] + '\n')
except FileNotFoundError:
    SelftosUtils.printf(f"<CONSOLE> Config file [red]not found[/red] at {CONFIG_PATH}, creating one...")
    try:
        with open(CONFIG_PATH, "w") as config_file:
            json.dump(example_config, config_file, indent=4)
    except:
        SelftosUtils.printf(f"<CONSOLE> [red]Error creating config file at {CONFIG_PATH}[/red]")
    else:
        SelftosUtils.printf(f"<CONSOLE> Config file created at {CONFIG_PATH}, please edit it and start the server.")
    exit(1)
except Exception as e:
    SelftosUtils.printf(f"<CONSOLE> [red]Error loading config file at {CONFIG_PATH} | {e}[/red]")
    exit(1)
else:
    SelftosUtils.printf(f"<CONSOLE> Config file loaded [green3]successfully[/green3]!")
    SelftosUtils.show_room_config(room_config)