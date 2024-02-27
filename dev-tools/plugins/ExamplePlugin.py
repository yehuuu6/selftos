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
