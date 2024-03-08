"""\
This module provides the necessary functions for your Selftos chat application.
"""

from io import StringIO
from rich.console import Console
from prompt_toolkit import ANSI, print_formatted_text
from typing import List
from rich.markup import escape

import library.network as SelftosNetwork
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

def printc(messages: List[str], executer: SelftosNetwork.User | None) -> None:
    """
    Prints output to the server console or to the console of the user who executed the command.
    """
    output = ""
    for line in messages:
        if line != messages[-1]:
            output += f"{line}\n"
        else:
            output += f"{line}"
    if executer is not None:
        package = SelftosNetwork.Package(type = "SFSMessage", content = output)
        SelftosNetwork.send_package(package, executer.sock)
    else:
        printf(output)

def get_user_by_socket(sock: socket.socket, users_list: List[SelftosNetwork.User]) -> SelftosNetwork.User | None:
    for user in users_list:
        if user.sock == sock:
            return user
    return None

def broadcast(prefix: str, users: List[SelftosNetwork.User], message: str, source: str | None = None, render_on_console: bool = False, exclude: SelftosNetwork.User | None = None) -> None:
    """
    Broadcast a message to all the users in the room.
    """
    if source is None:
        source = prefix
        
    for user in users:
        if source != prefix and source == user.name:
            role = user.main_role
            color = user.color
            # [[color]role[/color]] 
            perm_indicator = f"[gold3]{escape('[')}[/gold3][{color}]{role}[/{color}][gold3]{escape(']')}[/gold3] "
            break
    else:
        perm_indicator = ""
    
    source = f"[cyan]{source}[/cyan]" if source != prefix else source

    message = f"{perm_indicator}{source} {message}"
    if render_on_console:
        printf(message)
    for user in users:
        if user == exclude:
            continue
        package = SelftosNetwork.Package(type = "SFSMessage", content = message)
        SelftosNetwork.send_package(package, user.sock)

def is_space(msg) -> bool:
    """
    Returns True if the message contains only spaces.
    """
    for char in msg:
        if char != " ":
            return False
    return True