import library.network as SelftosNetwork
import library.general as SelftosGeneral
import utils.functions as SelftosUtils
import socket
import threading
import asyncio
import random
import string

from prompt_toolkit import PromptSession
from time import sleep

COMPUTER = socket.gethostname() # This is the computer name, used for the package source.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

is_running = False

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

user_id = generate_random_string(10)
user_name = input("User Name: ")

#IP = input("Server IP: ")
#PORT = int(input("Server Port: "))

IP = "localhost"
PORT = 7030

def package_handler(package: SelftosNetwork.Package) -> None:
    if not package.is_valid_package():
        SelftosUtils.printf("Invalid package received, something is wrong!")

    if package.type == "SFSHandshake" and package.content == "nickname":
        user_package = SelftosNetwork.Package(type = "SFSUserData", content = user.get_json())
        SelftosNetwork.send_package(user_package, client_socket)

    elif package.type == "SFSMessage":
        SelftosUtils.printf(f"{package.content}")

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
            if msg.startswith("/"):
                package = SelftosNetwork.Package(type = "SFSCommand", content = msg.replace("/", "", 1))
            else:
                package = SelftosNetwork.Package(type = "SFSMessage", content = msg)
            SelftosNetwork.send_package(package, client_socket)
        except Exception as e:
            SelftosUtils.printf("Error: " + str(e))
            is_running = False
            client_socket.close()
            input_loop.stop()
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
        client_socket.connect((IP, PORT))
        user = SelftosGeneral.User(id = user_id, name = user_name, sock = client_socket)
        is_running = True
    except ConnectionRefusedError:
        SelftosUtils.printf("Connection refused by the room.")
        sleep(3)
        exit(1)
    
    listen_thread = threading.Thread(target=listen, daemon=True)
    listen_thread.start()

def main() -> None:
    SelftosUtils.printf(f"Welcome {user_name}! Connecting to the room...")
    connect_to_room()
    global input_loop
    input_loop = asyncio.new_event_loop()  # Create a new event loop
    asyncio.set_event_loop(input_loop)  # Set it as the current event loop
    input_loop.create_task(write())
    input_loop.run_forever()

if __name__ == "__main__":
    main()