"""\
This module provides the necessary server classes for your Selftos chat application.
"""

import json
import socket

class User:
    """
    User object to store data about the user.
    """
    bans_list_path = "config/blacklist.txt"
    mutes_list_path = "config/mutelist.txt"
    admins_list_path = "config/admins.txt"

    def __init__(self, id: str, name: str, client: socket.socket):
        self.id = id
        self.name = name

        self.client = client
        self.address = client.getpeername()

        self.is_owner = False
        self.is_admin = self.get_user_status(self.admins_list_path)
        self.is_banned = self.get_user_status(self.bans_list_path)
        self.is_muted = self.get_user_status(self.mutes_list_path)

        self.role = self.set_role()

    def who(self) -> str:
        """
        Returns a readable string of the user's data.
        """
        return f"[orange1]ID:[/orange1] {self.id} - [orange1]Name:[/orange1] {self.name} - [orange1]Role:[/orange1] {self.role} - [orange1]Muted:[/orange1] {self.is_muted} - [orange1]From:[/orange1] {self.address}"
    
    def get_user_status(self, file_path: str) -> bool:
        with open(file_path, "r") as user_list:
            users = user_list.readlines()
            user_list.close()
        for user in users:
            if user.strip() == self.name:
                return True
        return False

    def set_role(self) -> str:
        """
        Sets the user's role.
        """
        if self.is_admin:
            return "Admin"
        else:
            return "User"

    def get_json(self) -> str:
        data = {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "is_banned": self.is_banned,
            "is_muted": self.is_muted,
            "is_admin": self.is_admin
        }
        return json.dumps(data)

    def ban(self) -> bool:
        # Check if the user is already banned and return false if so.
        with open(self.bans_list_path, "r") as ban_list:
            bans = [ban.strip() for ban in ban_list.readlines()]
        for ban in bans:
            if ban == self.name:
                return False
        # Else add the user to the bans list and return true.
        with open(self.bans_list_path, "a") as ban_list:
            ban_list.write(f"{self.name}\n")
        self.is_banned = True
        return True

    def mute(self) -> bool:
        # Check if the user is already muted and return false if so.
        with open(self.mutes_list_path, "r") as mute_list:
            mutes = [mute.strip() for mute in mute_list.readlines()]
        for mute in mutes:
            if mute == self.name:
                return False
        # Else add the user to the mutes list and return true.
        with open(self.mutes_list_path, "a") as mute_list:
            mute_list.write(f"{self.name}\n")
        self.is_muted = True
        return True

    def unmute(self) -> bool:
        mutes = []
        with open(self.mutes_list_path, "r") as mute_list:
            mutes = [mute.strip() for mute in mute_list.readlines()]
        
        # If the user is not muted, return false.
        if self.name not in mutes:
            return False

        with open(self.mutes_list_path, "w") as mute_list:
            for mute in mutes:
                if mute != self.name:
                    mute_list.write(mute + '\n')
        self.is_muted = False
        return True
    
    def admin(self) -> bool:
        # Check if the user is already an admin and return false if so.
        with open(self.admins_list_path, "r") as admin_list:
            admins = [admin.strip() for admin in admin_list.readlines()]
        for admin in admins:
            if admin == self.name:
                return False
        # Else add the user to the admins list and return true.
        with open(self.admins_list_path, "a") as admin_list:
            admin_list.write(f"{self.name}\n")
        self.is_admin = True
        self.role = self.set_role()
        return True

    def unadmin(self) -> bool:
        admins = []
        with open(self.admins_list_path, "r") as admin_list:
            admins = [admin.strip() for admin in admin_list.readlines()]
        
        # If the user is not an admin, return false.
        if self.name not in admins:
            return False

        # Write the updated admins list (excluding the self.name)
        with open(self.admins_list_path, "w") as admin_list:
            for admin in admins:
                if admin != self.name:
                    admin_list.write(admin + '\n')
        self.is_admin = False
        self.role = self.set_role()
        return True

    def disconnect(self) -> None:
        """
        Disconnects the user from the server.
        """
        self.client.close()

class Package:
    """
    Package object to send between the server and the client.
    """
    VALID_TYPES = [
        "SFSHandshake",
        "SFSMessage",
        "SFSHeartbeat",
        "SFSUserData",
        "SFSRoomData"
    ]

    def __init__(self, type: str, content: dict | str, source: str):
        self.type = type
        self.content = content
        self.source = source

    def is_valid_package(self) -> bool:
        """
        Checks if the package is valid.
        """
        if self.type not in self.VALID_TYPES:
            print("Invalid package type: " + self.type)
            return False
        return True

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

def get_package(sender: socket.socket) -> Package | None:
    """
    Receives a package as str from the sender and returns it as a Package.
    """
    try:
        response = sender.recv(2048).decode("utf-8")
    except socket.error:
        return None
    try:
        data = json.loads(response)
    except json.decoder.JSONDecodeError:
        # If client sends a long message, returns none, this will cause
        # the client to disconnect by force.
        return None

    package = Package(data["type"], data["content"], data["source"])

    return package

def send_package(package: Package, target: socket.socket) -> None:
    """
    Sends the package to the target as bytes.
    """
    data: str = json.dumps({
        "type": package.type,
        "content": package.content,
        "source": package.source
    })

    try:
        target.send(bytes(data, "utf-8"))
    except socket.error:
        pass