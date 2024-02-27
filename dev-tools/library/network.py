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
    bans_list_path = "config/banned-users.json"
    mutes_list_path = "config/muted-users.json"
    ops_list_path = "config/ops.json"
    roles_list_path = "config/core/roles.json"

    def __init__(self, id: str, name: str, sock: socket.socket):
        self.id = id
        self.name = name

        self.sock = sock
        self.address = sock.getpeername()

        self.is_op = self.get_user_status(self.ops_list_path)
        self.is_banned = self.get_user_status(self.bans_list_path)
        self.is_muted = self.get_user_status(self.mutes_list_path)
        self.color = "cyan"
        self.roles = self.set_roles()
        self.main_role = self.set_main_role()

    def who(self, detailed: bool = False) -> str:
        """
        Returns a readable string of the user's data.
        """
        return "DEV"
    
    def set_main_role(self) -> str:
        return "DEV"

    def get_user_status(self, file_path: str) -> bool:
        return False

    def set_roles(self) -> List[str]:
        """
        Sets the user's role based on the user's name, ordered by level.
        """
        return ["DEV"]

    def get_json(self) -> str:
        return "DEV"

    def ban(self) -> bool:
        """
        Ban the user from the server.
        """
        return False

    def op(self) -> bool:
        return False

    def mute(self) -> bool:
        """
        Mute the user.
        """
        return False
    
    def unmute(self) -> bool:
        """
        Unmute the user.
        """
        return False
    
    def deop(self) -> bool:
        """
        Deop the user.
        """
        return False

    def add_role(self, role_name: str) -> bool:
        """
        Give the user a role.
        """
        return False

    def remove_role(self, role_name: str) -> bool:
        """
        Remove a role from the user.
        """
        return False

    def has_permission(self, command: str, args: List[str]) -> bool:
        """
        Checks if the user has the for given command and arguments.
        """
        return False
    def disconnect(self) -> None:
        """
        Disconnects the user from the server.
        """
        return None

class Package:
    """
    Package object to send between the server and the client.
    """
    VALID_TYPES = [
        "SFSHandshake",
        "SFSMessage",
        "SFSCommand",
        "SFSHeartbeat",
        "SFSUserData",
        "SFSRoomData"
    ]

    def __init__(self, type: str, content: dict | str):
        self.type = type
        self.content = content

    def is_valid_package(self) -> bool:
        """
        Checks if the package is valid.
        """
        return False

class ServerPreview:
    """
    Server object that contains data about the server for server list window.
    """
    def __init__(self, ip: str, port: int, name: str, maxc: int, acvitec: int):
        self.ip = ip
        self.port = port
        self.name = name
        self.max_connections = maxc
        self.active_connections = acvitec
    
    def get_user_count(self) -> str:
        return f"{self.active_connections}/{self.max_connections}"

# Functions

def receive_all(sender: socket.socket) -> str:
    """
    Receives all the data from the sender and returns it as str.
    """
    return "DEV"

def get_package(sender: socket.socket) -> Package | None:
    """
    Receives a package as str from the sender and returns it as a Package.
    """

    return None

def send_package(package: Package, target: socket.socket) -> None:
    """
    Sends the package to the target as bytes.
    Known bug: If the package is being sent to a client just before the client's connection
    is closed by the server, the client will not receive the package. Because they will be
    disconnected before the package is received.
    """
    return None