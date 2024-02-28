# This is an example plugin for the Selftos server you can create your own plugins by following this example.

from typing import List

import library.network as SelftosNetwork # Has classes like User, Package, etc.
import utils.functions as SelftosUtils # Has functions like printf, printc, broadcast, etc.
import socket

class ExamplePlugin:
    def __init__(self):
        """
        Constructor for the plugin.
        Everything here is required, do not remove anything.
        You can add more attributes if you need.
        """
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.description = "An example plugin for the Selftos server"
        self.author = "yehuuu6"
        self.prefix = "<[cyan]ExamplePlugin[/cyan]>"
        self.online_users: List[SelftosNetwork.User] = []

    def on_package_received(self, client_sock: socket.socket, package: SelftosNetwork.Package) -> bool:
        """
        Called when a package is received from a client.
        Cancellable: Yes
        :param client_sock: The socket of the client
        :param package: The package that was received
        :return: False to cancel the received package processing, True to continue normally
        """
        return True

    def on_message_received(self, user: SelftosNetwork.User, message: str) -> bool:
        """
        Called when a user sends a message.
        Cancellable: Yes
        :param user: The user who sent the message
        :param message: The message that was sent
        :return: False to cancel the message broadcast, True to continue normally
        """
        return True

    def on_user_joined(self, user: SelftosNetwork.User) -> None:
        """
        Called when a user joins the server.
        Cancellable: No
        :param user: The user who joined the server
        """

    def on_user_left(self, user: SelftosNetwork.User) -> None:
        """
        Called when a user leaves the server.
        Cancellable: No
        :param user: The user who left the server
        """
        pass

    def on_command_executed(self, user: SelftosNetwork.User, command: str, args: List[str]) -> bool:
        """
        Called when a command is executed by a user.
        Cancellable: Yes
        :param user: The user who executed the command
        :param command: The command that was executed
        :param args: The arguments of the command
        :return: False to cancel the command, True to continue normally
        """
        return True

# Entry point for the plugin, name must be PyInit_<plugin_name> and match the file name.
def PyInit_ExamplePlugin():
    return ExamplePlugin()
