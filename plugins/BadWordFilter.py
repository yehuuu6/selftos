from typing import List

import library.network as SelftosNetwork
import utils.functions as SelftosUtils
import socket

class BadWordFilter:
    def __init__(self):
        self.name = "Bad Word Filter"
        self.version = "1.0.0"
        self.description = "A simple bad word filter that kicks users if they use bad words in the chat."
        self.author = "yehuuu6"
        self.prefix = "<[red3]BadWordFilter[/red3]>"
        self.online_users: List[SelftosNetwork.User] = []

    def broadcast(self, message: str, render_on_server: bool = False, exclude: SelftosNetwork.User | None = None):
        message = f"{self.prefix} {message}"  # Add the prefix to the message
        if render_on_server:
            SelftosUtils.printf(message)
        for user in self.online_users:
            if user == exclude:
                continue
            msg_package = SelftosNetwork.Package(type="SFSMessage", content=message)
            try:
                SelftosNetwork.send_package(package=msg_package, target=user.sock)
            except:
                SelftosUtils.printf(f"<{self.prefix}> Failed to send message to [cyan]{user.name}[/cyan]")

    def on_package_received(self, client_sock: socket.socket, package: SelftosNetwork.Package) -> bool:
        return True

    def on_message_received(self, user: SelftosNetwork.User, message: str) -> bool:
        bad_words = ["badword1", "badword2", "badword3"]
        for bad_word in bad_words:
            if bad_word in message:
                self.broadcast(f"{user.name} used a bad word and was kicked from the server.", render_on_server=True, exclude=user)
                inform_package = SelftosNetwork.Package(type="SFSMessage", content=f"{self.prefix} You have been kicked out for using bad words!")
                SelftosNetwork.send_package(package=inform_package, target=user.sock)
                user.disconnect()
                return False
        return True

    def on_user_joined(self, user: SelftosNetwork.User) -> None:
        pass
    def on_user_left(self, user: SelftosNetwork.User) -> None:
        pass
    def on_command_executed(self, user: SelftosNetwork.User, command: str, args: List[str]) -> bool:
        return True

# Entry point for initializing the module
def PyInit_BadWordFilter():
    return BadWordFilter()
