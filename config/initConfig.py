import json

CONFIG_PATH = "config/selftos.config.json"

example_config: dict ={
    "host": "localhost",
    "port": 7030,
    "name": "Selftos Chat Room",
    "description": "A chat room for Selftos!",
    "maxUsers": 5,
    "private": False,
    "password": None,
    "owner": None,
    "show_muted_messages": True,
    "message_logging": True,
}

try:
    with open(CONFIG_PATH) as config_file:
        room_config: dict = json.load(config_file)
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


    config_file.close()
except FileNotFoundError:
    print(f"Config file not found at {CONFIG_PATH}, creating one...")
    try:
        with open(CONFIG_PATH, "w") as config_file:
            json.dump(example_config, config_file, indent=4)
    except:
        print(f"Error creating config file at {CONFIG_PATH}")
    else:
        print(f"Config file created at {CONFIG_PATH}, please edit it and start the server.")
    exit(1)
except:
    print(f"Error loading config file at {CONFIG_PATH}")
    exit(1)
