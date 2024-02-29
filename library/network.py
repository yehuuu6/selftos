"""\
This module provides the necessary server classes for your Selftos chat application.
"""

import json
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

        self.is_op = self.__get_user_status(self.ops_list_path)
        self.is_banned = self.__get_user_status(self.bans_list_path)
        self.is_muted = self.__get_user_status(self.mutes_list_path)
        self.color = "cyan"
        self.roles = self.__set_roles()
        self.main_role = self.__set_main_role()

    def who(self, detailed: bool = False) -> str:
        """
        Returns a readable string of the user's data.
        """
        if detailed:
            output = f"[orange1]ID:[/orange1] {self.id} - [orange1]Name:[/orange1] {self.name} - [orange1]Roles[/orange1]: {', '.join(self.roles)} - [orange1]Operator:[/orange1] {self.is_op} - [orange1]Muted:[/orange1] {self.is_muted} - [orange1]From:[/orange1] {self.address}"
        else:
            output = f"[orange1]ID:[/orange1] {self.id} - [orange1]Name:[/orange1] {self.name} - [orange1]Role[/orange1]: {self.main_role}"
        return output
    
    def __set_main_role(self) -> str:
        role = self.roles[-1] # The last role in the list is the main role
        return role

    def __get_user_status(self, file_path: str) -> bool:
        with open(file_path, "r") as user_list:
            users = json.load(user_list)
        for user in users:
            if user["name"] == self.name:
                return True
        return False

    def __set_roles(self) -> List[str]:
        """
        Sets the user's role based on the user's name, ordered by level.
        """
        user_roles = []
        user_colors = []
        with open(self.roles_list_path, "r") as roles_list:
            roles = json.load(roles_list)

        # Filter roles based on the user's name and store them in a list
        for role in roles:
            if role.get("default") == True:
                user_colors.append((role["level"], role["color"]))
                user_roles.append((role["level"], role["name"]))
            for user in role.get("users", []):
                if user.get("name") == self.name:
                    user_colors.append((role["level"], role["color"]))
                    user_roles.append((role["level"], role["name"]))

        # Sort roles based on their level
        user_roles.sort(key=lambda x: x[0])
        user_colors.sort(key=lambda x: x[0])

        # Extract role names from the sorted list
        sorted_roles = [role_name for _, role_name in user_roles]
        sorted_colors = [role_color for _, role_color in user_colors]

        self.color = sorted_colors[-1] # The last role in the list is the main role

        return sorted_roles

    def get_json(self) -> str:
        data = {
            "id": self.id,
            "name": self.name,
            "roles": self.roles,
            "is_banned": self.is_banned,
            "is_muted": self.is_muted,
            "is_op": self.is_op
        }
        return json.dumps(data)

    def ban(self) -> bool:
        """
        Ban the user from the server.
        """
        add = {
            "uid": self.id,
            "name": self.name
        }

        # Check if the user is already banned by checking the bans.json file.
        with open(self.bans_list_path, "r") as bans_list:
            bans = json.load(bans_list)
        for ban in bans:
            if ban["name"] == self.name:
                return False
        # Else add the user to the bans list and return true.
        with open(self.bans_list_path, "w") as bans_list:
            bans.append(add)
            json.dump(bans, bans_list, indent=2)
        
        self.is_banned = True

        return True

    def op(self) -> bool:
        # Check if the user is already op by checking the ops.json file.
        with open(self.ops_list_path, "r") as ops_list:
            ops = json.load(ops_list)
        for op in ops:
            if op["name"] == self.name:
                return False
        # Else add the user to the ops list and return true.
        with open(self.ops_list_path, "w") as ops_list:
            obj = {
                "uid": self.id,
                "name": self.name
            }
            ops.append(obj)
            json.dump(ops, ops_list, indent=2)
        
        self.is_op = True

        return True

    def mute(self) -> bool:
        """
        Mute the user.
        """
        add = {
            "uid": self.id,
            "name": self.name
        }

        # Check if the user is already muted by checking the mutes.json file.
        with open(self.mutes_list_path, "r") as mutes_list:
            mutes = json.load(mutes_list)
        for mute in mutes:
            if mute["name"] == self.name:
                return False
        # Else add the user to the mutes list and return true.
        with open(self.mutes_list_path, "w") as mutes_list:
            mutes.append(add)
            json.dump(mutes, mutes_list, indent=2)
        
        self.is_muted = True

        return True
    
    def unmute(self) -> bool:
        """
        Unmute the user.
        """
        with open(self.mutes_list_path, "r") as mutes_list:
            mutes = json.load(mutes_list)
        for mute in mutes:
            if mute["name"] == self.name:
                mutes.remove(mute)
                break
        else:
            return False
        with open(self.mutes_list_path, "w") as mutes_list:
            json.dump(mutes, mutes_list, indent=2)
        
        self.is_muted = False
        return True
    
    def deop(self) -> bool:
        """
        Deop the user.
        """
        with open(self.ops_list_path, "r") as ops_list:
            ops = json.load(ops_list)
        for op in ops:
            if op["name"] == self.name:
                ops.remove(op)
                break
        else:
            return False
        with open(self.ops_list_path, "w") as ops_list:
            json.dump(ops, ops_list, indent=2)
        
        self.is_op = False
        return True

    def add_role(self, role_name: str) -> bool:
        """
        Give the user a role.
        """
        with open(self.roles_list_path, "r") as roles_list:
            roles = json.load(roles_list)
        for role in roles:
            if role.get("default") == True:
                continue
            if str(role["name"]) == role_name:
                for user in role.get("users", []):
                    if user.get("name") == self.name:
                        return False
                role["users"].append({
                    "uid": self.id,
                    "name": self.name
                })
                break
        else:
            return False
        try:
            with open(self.roles_list_path, "w") as roles_list:
                json.dump(roles, roles_list, indent=2)
        except PermissionError:
            return False
        
        self.roles = self.__set_roles()
        self.main_role = self.__set_main_role()

        return True

    def remove_role(self, role_name: str) -> bool:
        """
        Remove a role from the user.
        """
        with open(self.roles_list_path, "r") as roles_list:
            roles = json.load(roles_list)
        for role in roles:
            if role.get("default") == True:
                continue
            if str(role["name"]) == role_name:
                for user in role.get("users", []):
                    if user.get("name") == self.name:
                        role["users"].remove(user)
                        break
                else:
                    return False
                break
        else:
            return False
        try:
            with open(self.roles_list_path, "w") as roles_list:
                json.dump(roles, roles_list, indent=2)
        except PermissionError:
            return False
        
        self.roles = self.__set_roles()
        self.main_role = self.__set_main_role()

        return True

    def has_permission(self, command: str, args: List[str]) -> bool:
        """
        Checks if the user has the for given command and arguments.
        """
        if self.is_op:
            return True
        for role in self.roles:
            with open(self.roles_list_path, "r") as roles_list:
                roles = json.load(roles_list)
            for role_data in roles:
                if role_data["name"] == role:
                    if command in role_data["permissions"]:
                        if len(args) == 0:
                            return True
                        if "*" in role_data["permissions"][command]:
                            return True
                        for arg in args:
                            if arg in role_data["permissions"][command]:
                                return True
        return False
    def disconnect(self) -> None:
        """
        Disconnects the user from the server.
        """
        self.sock.close()

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
        if self.type not in self.VALID_TYPES:
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

HEADER_SIZE = 10

def receive_all(sender: socket.socket) -> str:
    """
    Receives all the data from the sender and returns it as str.
    """
    full_msg = ""
    new_msg = True
    msg_len = 0
    while True:
        msg = sender.recv(16)
        if new_msg:
            msg_len = int(msg[:HEADER_SIZE])
            new_msg = False

        full_msg += msg.decode("utf-8")

        if len(full_msg) - HEADER_SIZE == msg_len:
            break

    return full_msg[HEADER_SIZE:]

def get_package(sender: socket.socket) -> Package | None:
    """
    Receives a package as str from the sender and returns it as a Package.
    """
    try:
        #response = receive_all(sender)
        response = sender.recv(4096).decode("utf-8")
    except socket.error:
        return None
    try:
        data = json.loads(response)
    except json.decoder.JSONDecodeError:
        # If client sends a long message, returns none, this will cause
        # the client to disconnect by force.
        return None

    package = Package(data["type"], data["content"])

    return package

def send_package(package: Package, target: socket.socket) -> None:
    """
    Sends the package to the target as bytes.
    Known bug: If the package is being sent to a client just before the client's connection
    is closed by the server, the client will not receive the package. Because they will be
    disconnected before the package is received.
    """
    data: str = json.dumps({
        "type": package.type,
        "content": package.content
    })

    #data = f"{len(data):<{HEADER_SIZE}}" + data

    try:
        target.send(bytes(data, "utf-8"))
    except socket.error:
        pass