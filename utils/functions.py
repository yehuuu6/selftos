"""\
This module provides the necessary functions for your Selftos chat application.
"""

from io import StringIO
from rich.console import Console
from prompt_toolkit import ANSI, print_formatted_text
from typing import List

import classes.network as SelftosNetwork
import socket
import time

output_buffer = StringIO()
console = Console(file=output_buffer, color_system="truecolor")

def clear_console() -> None:
    """
    Clears the server console.
    """
    print("\033[H\033[J", end='')  # ANSI escape sequence to clear the console

def get_current_time() -> str:
    """
    Returns the current time in HH:MM format.
    """
    return time.strftime("%H:%M:%S", time.localtime(time.time()))

def printf(msg: str) -> None:
    """
    Prints output to the server console.
    """
    output_buffer.seek(0)  # Reset the buffer to the beginning
    output_buffer.truncate(0)  # Clear the buffer content
    console.print(f"[white]{get_current_time()}[/white] {msg}")
    print_formatted_text(ANSI(output_buffer.getvalue()), end='')

def printc(msg: str, executer: SelftosNetwork.User | None) -> None:
    """
    Prints output to the server console or to the console of the user who executed the command.
    """
    if executer is not None:
        package = SelftosNetwork.Package(type = "SFSMessage", content = msg, source = "[magenta]SERVER[/magenta]")
        SelftosNetwork.send_package(package, executer.client)
    else:
        printf(msg)

def show_room_config(config: dict) -> None:
    printf(f"<CONSOLE> Host is set to [bold yellow]{config['host']}[/bold yellow].")
    printf(f"<CONSOLE> Port is set to [bold yellow]{config['port']}[/bold yellow].")
    printf(f"<CONSOLE> ID is set to [bold yellow]{config['id']}[/bold yellow].")
    printf(f"<CONSOLE> Name is set to [bold yellow]{config['name']}[/bold yellow].")
    printf(f"<CONSOLE> Description is set to [bold yellow]{config['description']}[/bold yellow].")
    printf(f"<CONSOLE> Maximum number of users is set to [bold yellow]{config['maxUsers']}[/bold yellow].")
    printf(f"<CONSOLE> Private is set to [bold yellow]{config['private']}[/bold yellow].")
    printf(f"<CONSOLE> Owner is set to [bold yellow]{config['owner']['name']}[/bold yellow].")
    printf(f"<CONSOLE> Show muted messages is set to [bold yellow]{config['show_muted_messages']}[/bold yellow].")
    printf(f"<CONSOLE> Message logging is set to [bold yellow]{config['message_logging']}[/bold yellow].")
    printf(f"<CONSOLE> Loading roles...")
    printf(f"<CONSOLE> Default role is set to [bold yellow]{config['default_role']}[/bold yellow].")
    for role in config['roles']:
        printf(f"<CONSOLE> [bold yellow]{role['name']}[/bold yellow] role is ready!")
def get_user_by_socket(sock: socket.socket, users_list: List[SelftosNetwork.User]) -> SelftosNetwork.User | None:
    for user in users_list:
        if user.client == sock:
            return user
    return None