"""\
This module provides the necessary server classes for your Selftos chat application.
"""

import socket as sck

from typing import List

class User:
    def __init__(self, id: str, name: str, sock: sck.socket) -> None:
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

    def who(self, detailed: bool = False) -> str: ...

    def get_json(self) -> str: ...

    def ban(self) -> bool: ...

    def op(self) -> bool: ...

    def mute(self) -> bool: ...
    
    def unmute(self) -> bool: ...
    
    def deop(self) -> bool: ...

    def add_role(self, role_name: str) -> bool: ...

    def remove_role(self, role_name: str) -> bool: ...

    def has_permission(self, command: str, args: List[str]) -> bool: ...
    
    def disconnect(self) -> None: ...

class Package:
    def __init__(self, type: str, content: dict | str) -> None:
        self.type = type
        self.content = content

    def is_valid_package(self) -> bool: ...

# Functions

def get_package(sender: sck.socket) -> Package | None: ...

def send_package(package: Package, target: sck.socket) -> None: ...