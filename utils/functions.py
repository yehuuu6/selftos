"""\
This module provides the necessary functions for your Selftos chat application.
"""

from io import StringIO
from rich.console import Console
from prompt_toolkit import ANSI, print_formatted_text
from typing import List

import classes.SelftosNetwork as SelftosNetwork
import socket

output_buffer = StringIO()
console = Console(file=output_buffer, color_system="truecolor")

def clear_console() -> None:
    """
    Clears the server console.
    """
    print("\033[H\033[J", end='')  # ANSI escape sequence to clear the console

def printf(msg: str) -> None:
    """
    Prints output to the server console.
    """
    output_buffer.seek(0)  # Reset the buffer to the beginning
    output_buffer.truncate(0)  # Clear the buffer content
    console.print(msg)
    print_formatted_text(ANSI(output_buffer.getvalue()), end='')

def show_room_config(config: dict) -> None:
    for key, value in config.items():
        key = key.capitalize()
        printf(f"<SERVER> {key}: {value}")

def get_user_by_socket(sock: socket.socket, users_list: List[SelftosNetwork.User]) -> SelftosNetwork.User | None:
    for user in users_list:
        if user.client == sock:
            return user
    return None