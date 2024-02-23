from typing import List

import classes.network as SelftosNetwork
import utils.functions as SelftosUtils
import socket

class ExamplePlugin():
    def __init__(self):
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.description = "An example plugin for the Selftos server"
        self.author = "yehuuu6"
        self.prefix = "[cyan]ExamplePlugin[/cyan]"
        self.online_users: List[SelftosNetwork.User] = []
        SelftosUtils.printf(f"<CONSOLE> Example Plugin loaded [green3]successfully[/green3]!")
    def broadcast(self, message: str, render_on_server: bool = False, exclude: SelftosNetwork.User | None = None):
        if render_on_server:
            SelftosUtils.printf(message)
        for user in self.online_users:
            if user == exclude:
                continue
            msg_package = SelftosNetwork.Package(type="SFSMessage", content= message, source=f"<{self.prefix}>")
            try:
                SelftosNetwork.send_package(package=msg_package, target=user.client)
            except:
                SelftosUtils.printf(f"<{self.prefix}> Failed to send message to [cyan]{user.name}[/cyan]")

    def on_package_received(self, client_sock: socket.socket, package: SelftosNetwork.Package):
        pass
    def on_message_received(self, user: SelftosNetwork.User, message: str):
        pass
    def on_user_joined(self, user:SelftosNetwork.User):
        self.online_users.append(user)
    def on_user_left(self, user:SelftosNetwork.User):
        self.online_users.remove(user)
    def on_command_executed(self, user: SelftosNetwork.User, command: str, args: List[str]):
        pass