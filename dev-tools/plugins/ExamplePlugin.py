# This is an example plugin for the Selftos server you can create your own plugins by following this example.

from typing import List

import library.network as SelftosNetwork
import utils.functions as SelftosUtils
import socket

class ExamplePlugin:
    def __init__(self):
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.description = "An example plugin for the Selftos server"
        self.author = "yehuuu6"
        self.prefix = "<[cyan]ExamplePlugin[/cyan]>"
        self.online_users: List[SelftosNetwork.User] = []

    def set_online_users(self, users_from_server: List[SelftosNetwork.User] = []) -> None:
        self.online_users = users_from_server

    def broadcast(self, message: str, render_on_server: bool = False, exclude: SelftosNetwork.User | None = None):
        message = f"{self.prefix} {message}"  # Add the prefix to the message
        if render_on_server:
            SelftosUtils.printf(message)
        for user in self.online_users:
            if user == exclude:
                continue
            msg_package = SelftosNetwork.Package(type="SFSMessage", content=message, source=f"<{self.prefix}>")
            try:
                SelftosNetwork.send_package(package=msg_package, target=user.client)
            except:
                SelftosUtils.printf(f"<{self.prefix}> Failed to send message to [cyan]{user.name}[/cyan]")

    def on_package_received(self, client_sock: socket.socket, package: SelftosNetwork.Package) -> bool:
        return True

    def on_message_received(self, user: SelftosNetwork.User, message: str) -> bool:
        return True

    def on_user_joined(self, user: SelftosNetwork.User) -> None:
        pass

    def on_user_left(self, user: SelftosNetwork.User) -> None:
        pass

    def on_command_executed(self, user: SelftosNetwork.User, command: str, args: List[str]) -> bool:
        return True

# Entry point for initializing the module
def PyInit_ExamplePlugin():
    return ExamplePlugin()
