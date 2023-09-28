import classes.SelftosNetwork as SelftosNetwork
import classes.SelftosClient as SelftosClient
import utils.functions as SelftosUtils
import socket
import threading

from prompt_toolkit import PromptSession
import asyncio
import random
import string


COMPUTER = socket.gethostname() # This is the computer name, used for the package source.

FILE_TYPE = "CLIENT" # This is the sender type for the package. MAYBE WE CAN USE THIS AS USER NAME SO WE DONT HAVE TO SEARCH FOR IT IN THE SERVER.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

is_running = False

# Asyncio loop
input_loop = asyncio.get_event_loop()

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

user_id = generate_random_string(10)
user_name = input("User Name: ")

def package_handler(package: SelftosNetwork.Package) -> None:
    if not package.is_valid_package():
        SelftosUtils.printf("Invalid package received, something is wrong!")

    if package.type == "SFSHandshake" and package.content == "nickname":
        user_package = SelftosNetwork.Package(type = "SFSUserData", content = user.get_json(), source = FILE_TYPE)
        SelftosNetwork.send_package(user_package, client_socket)

    elif package.type == "SFSMessage":
        SelftosUtils.printf(f"<[cyan]{package.source}[/cyan]> {package.content}")

async def write() -> None:
    global is_running

    session = PromptSession(user.name + f"@{COMPUTER}" + r"\~ ", erase_when_done=True)

    while is_running:
        try:
            try:
                msg = await session.prompt_async()
            except (EOFError, KeyboardInterrupt):
                is_running = False
                input_loop.stop()
                client_socket.close()
                break
            msg = f"{msg}"
            package = SelftosNetwork.Package(type = "SFSMessage", content = msg, source = FILE_TYPE)
            SelftosNetwork.send_package(package, client_socket)
        except Exception as e:
            SelftosUtils.printf("Error: " + str(e))
            is_running = False
            client_socket.close()
            break

def listen() -> None:
    global is_running
    while is_running:
        try:
            package = SelftosNetwork.get_package(client_socket)
            if package == None:
                continue
            package_handler(package)

        except socket.error:
            SelftosUtils.printf("An error occured!")
            input_loop.stop()
            is_running = False
            client_socket.close()
            break

def connect_to_room() -> None:
    global is_running
    global user
    try:
        client_socket.connect(("127.0.0.1", 7033))
        user = SelftosClient.User(id = user_id, name = user_name, client = client_socket)
        is_running = True
    except ConnectionRefusedError:
        SelftosUtils.printf("Connection refused by the room.")
        exit(1)
    
    listen_thread = threading.Thread(target=listen, daemon=True)
    listen_thread.start()

def main() -> None:
    SelftosUtils.printf(f"Welcome {user_name}! Connecting to the room...")
    connect_to_room()
    input_loop.create_task(write())
    input_loop.run_forever()

if __name__ == "__main__":
    main()