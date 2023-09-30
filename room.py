from typing import List
from prompt_toolkit import PromptSession
from rich.markup import escape
import utils.commands as SelftosCommands

import config.loader as SelftosConfig
import utils.functions as SelftosUtils
import classes.network as SelftosNetwork
import socket
import threading
import json
import asyncio

config = SelftosConfig.config

PREFIX = "[magenta]SERVER[/magenta]" # This is a server, not client.
OWNER = config['owner']
PROMPT_PREFIX = f"{config['id']}"

selftos_main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #  Main Server
room_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Room Server Socket
is_running = False # Is the server running?
users_list: List[SelftosNetwork.User] = [] # List of users in the room
input_loop = asyncio.get_event_loop() # Asyncio loop for the admin input

def connect_main_server() -> None:
    """
    Connects to Selftos main server
    """
    MAIN_HOST = "192.168.1.10"
    MAIN_PORT = 7030
    try:
        selftos_main_socket.connect((MAIN_HOST, MAIN_PORT))
    except ConnectionRefusedError:
        SelftosUtils.printf("<CONSOLE> [red]Connection refused by the main server.[/red]")
        exit(1)

def shutdown(users = users_list, reason: str = "No reason was specified.") -> None:
    """
    Terminates the server with the specified reason.
    """
    global is_running
    SelftosCommands.broadcast(users, f"Shutting down! [yellow]({reason})[/yellow]", render_on_console=True)
    for user in users:
        user.disconnect()
    is_running = False
    input_loop.stop()
    users.clear()
    room_socket.close()

def package_handler(package: SelftosNetwork.Package, sender: socket.socket) -> None:
    """
    Manages received packages.
    """
    if not package.is_valid_package():
        SelftosUtils.printf("<CONSOLE> Invalid package received, something is wrong!")
        _package = SelftosNetwork.Package(type = "SFSMessage", content = "You have send an invalid package. Connection will be closed.", source = PREFIX)
        SelftosNetwork.send_package(_package, sender)
        sender.close()

    if package.type == "SFSUserData":
        user_data: dict = json.loads(str(package.content))
        user_id = user_data["id"]
        user_name = user_data["name"]

        user = SelftosNetwork.User(id = user_id, name = user_name, client = sender)

        if user.is_banned:
            banned_inform_package = SelftosNetwork.Package(type = "SFSMessage", content = "[red3]You are banned from this room![/red3]", source = PREFIX)
            SelftosNetwork.send_package(banned_inform_package, sender)
            user.disconnect()
            SelftosUtils.printf(f"<CONSOLE> [cyan]{user.name}[/cyan] tried to join the room, but they are [red]banned[/red].")
            return

        users_list.append(user)

        if user.name == OWNER:
            user.is_op = True
            SelftosCommands.broadcast(users_list, f"Attention! an [red3]oeprator[/red3] is joining to the room.", render_on_console=True)

        SelftosCommands.broadcast(users_list, f"[cyan]{user.name}[/cyan] has joined the room.", render_on_console=True, exclude=user)

    elif package.type == "SFSMessage":
        user = SelftosUtils.get_user_by_socket(sender, users_list)
        if user is None:
            SelftosUtils.printf("<CONSOLE> [red]Error: User not found.[/red]")
            return
        if user.is_muted:
            muted_inform_package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{PREFIX}> You are muted.", source = PREFIX)
            SelftosNetwork.send_package(muted_inform_package, sender)
            if config['show_muted_messages']:
                SelftosUtils.printf(f"[red]MUTED[/red] | <[cyan]{user.name}[/cyan]> [strike]{escape(str(package.content))}[/strike]")
            return
        SelftosCommands.broadcast(users_list, f"{escape(str(package.content))}", msg_source=f"[cyan]{user.name}[/cyan]", render_on_console=True)

def client_handler(client: socket.socket, address: tuple) -> None:
    while is_running:
        package = SelftosNetwork.get_package(client)
        if package is not None:
            package_handler(package, client)
        else:
            if is_running:
                SelftosUtils.printf(f"<CONSOLE> Connection from {address} has been lost.")
                user = SelftosUtils.get_user_by_socket(client, users_list)
                if user is not None:
                    users_list.remove(user)
                    SelftosCommands.broadcast(users_list, f"[cyan]{user.name}[/cyan] has left the room.", render_on_console=True)
            break

def connection_handler() -> None:
    while is_running:
        try:
            client_socket, address = room_socket.accept()
            SelftosUtils.printf(f"<CONSOLE> Connection from {address} has been established.")

            client_handler_thread = threading.Thread(target=client_handler, args=(client_socket, address), daemon=True)
            client_handler_thread.start()

            package = SelftosNetwork.Package(type = "SFSHandshake", content = "nickname", source = PREFIX) # TODO: Give server info to the client in content.
            SelftosNetwork.send_package(package, client_socket)

        except socket.error as e:
            if (not is_running):
                break
            else:
                print(f"<[red]ERROR[/red]> Failed to accept connection: {e}")
        except KeyboardInterrupt:
            shutdown()
            break

async def handle_admin_input() -> None:

    session = PromptSession(f"console@{PROMPT_PREFIX}" + r"\~ ", erase_when_done=True)

    while is_running:  
        try:
            cin = await session.prompt_async()
        except (EOFError, KeyboardInterrupt):
            shutdown()
            break

        input_list = cin.strip().split(' ')
        command: str = input_list[0]
        args: List[str] = input_list[1:]

        if command == "shutdown":
            if len(args) == 0:
                shutdown()
            else:
                s_msg = " ".join(args)
                shutdown(reason=s_msg)
        else:
            requested_command = SelftosCommands.COMMANDS.get(command)
            if requested_command is None:
                SelftosUtils.printf(f"<CONSOLE> Command [red]'{command}'[/red] not found. Type 'help' to list commands.")
                continue
            else:
                requested_command(users_list, args)

def start() -> None:
    global is_running
    #connect_main_server()
    try:
        room_socket.bind((config['host'], config['port']))
        room_socket.listen(config['maxUsers'])

        is_running = True

        connection_handler_thread = threading.Thread(target=connection_handler, daemon=True)
        connection_handler_thread.start()
    except Exception as e:
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Can not start the server: {e}[/red]")
        exit(1)
    else:
        SelftosUtils.printf(f"<CONSOLE> Server is [green3]online[/green3] and listening on {config['host']}:{config['port']}")
    
def main():
    SelftosUtils.printf("<CONSOLE> Starting the room server...")
    start()
    input_loop.create_task(handle_admin_input())
    input_loop.run_forever()

if __name__ == "__main__":
    main()