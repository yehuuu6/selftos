"""\
This module provides the necessary functions for your Selftos chat application.
"""
### DO NOT MODIFY THIS FILE IT IS FOR TYPE HINTING ONLY THE REAL FILE IS IN THE SERVER ###
### DO NOT MODIFY THIS FILE IT IS FOR TYPE HINTING ONLY THE REAL FILE IS IN THE SERVER ###
### DO NOT MODIFY THIS FILE IT IS FOR TYPE HINTING ONLY THE REAL FILE IS IN THE SERVER ###
### DO NOT MODIFY THIS FILE IT IS FOR TYPE HINTING ONLY THE REAL FILE IS IN THE SERVER ###

from io import StringIO
from rich.console import Console
from typing import List

import library.network as SelftosNetwork
import socket

output_buffer = StringIO()
console = Console(file=output_buffer, color_system="truecolor")

def clear_console() -> None:
    """
    Clears the server console.
    """
    return None

def get_current_time() -> str:
    """
    Returns the current time in HH:MM format.
    """
    return "00:00:00"

def printf(msg: str) -> None:
    """
    Prints output to the server console.
    """
    return None

def printc(messages: List[str], executer: SelftosNetwork.User | None) -> None:
    """
    Prints output to the server console or to the console of the user who executed the command.
    """
    return None

def get_user_by_socket(sock: socket.socket, users_list: List[SelftosNetwork.User]) -> SelftosNetwork.User | None:
    return None

def broadcast(prefix: str, users: List[SelftosNetwork.User], message: str, source: str | None = None, render_on_console: bool = False, exclude: SelftosNetwork.User | None = None) -> None:
    """
    Broadcast a message to all the users in the room.
    """
    return None