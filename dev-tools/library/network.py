"""\
This module provides the necessary server classes for your Selftos chat application.
"""
### DO NOT MODIFY THIS FILE IT IS FOR TYPE HINTING ONLY THE REAL FILE IS IN THE SERVER ###
### DO NOT MODIFY THIS FILE IT IS FOR TYPE HINTING ONLY THE REAL FILE IS IN THE SERVER ###
### DO NOT MODIFY THIS FILE IT IS FOR TYPE HINTING ONLY THE REAL FILE IS IN THE SERVER ###
### DO NOT MODIFY THIS FILE IT IS FOR TYPE HINTING ONLY THE REAL FILE IS IN THE SERVER ###

import socket

from typing import List

class User:
    """
    User object to store data about the user.
    """

    def __init__(self, id: str, name: str, sock: socket.socket):
        self.id = id
        self.name = name

        self.sock = sock
        self.address = sock.getpeername()

        self.is_op = False
        self.is_banned = False
        self.is_muted = False
        self.color = "cyan"
        self.roles = []
        self.main_role = ""

    def who(self, detailed: bool = False) -> str:
        """
        Returns a readable string of the user's data.
        """
        return "DEV"

    def get_json(self) -> str:
        """
        Returns the user's data as a JSON string.
        """
        return "DEV"

    def ban(self) -> bool:
        """
        Ban the user from the server.
        """
        return True

    def op(self) -> bool:
        return True

    def mute(self) -> bool:
        """
        Mute the user.
        """
        return True
    
    def unmute(self) -> bool:
        """
        Unmute the user.
        """
        return True
    
    def deop(self) -> bool:
        """
        Deop the user.
        """
        return True

    def add_role(self, role_name: str) -> bool:
        """
        Give the user a role.
        """
        return True

    def remove_role(self, role_name: str) -> bool:
        """
        Remove a role from the user.
        """
        return True

    def has_permission(self, command: str, args: List[str]) -> bool:
        """
        Checks if the user has the for given command and arguments.
        """
        return True
    
    def disconnect(self) -> None:
        """
        Disconnects the user from the server.
        """
        return None

class Package:
    """
    Package object to send between the server and the client.
    """
    VALID_TYPES = []

    def __init__(self, type: str, content: dict | str):
        self.type = type
        self.content = content

    def is_valid_package(self) -> bool:
        """
        Checks if the package is valid.
        """
        return True

# Functions

def get_package(sender: socket.socket) -> Package | None:
    """
    Receives a package as str from the sender and returns it as a Package.
    """
    return None

def send_package(package: Package, target: socket.socket) -> None:
    """
    Sends the package to the target as bytes.
    """
    return None