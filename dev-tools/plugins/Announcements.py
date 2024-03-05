from typing import List

import library.network as SelftosNetwork # Has classes like User, Package, etc.
import utils.functions as SelftosUtils # Has functions like printf, printc, broadcast, etc.
import socket
import time
import threading as th
import random

# Threads continue even after the plugin is unloaded. Make sure to stop them when the plugin is unloaded.
# Threads causes server to not stop properly on shutdown. Make sure to stop them when the server is shutting down.

class Announcements:
    def __init__(self):
        """
        Constructor for the plugin.
        Everything here is required, do not remove anything.
        You can add more attributes if you need.
        """
        self.name = "Announcements"
        self.version = "1.0.1"
        self.description = "A plugin for sending announcements to the server users at a specific interval."
        self.author = "yehuuu6"
        self.prefix = "<[aquamarine1]Announcements[/aquamarine1]>"
        self.online_users: List[SelftosNetwork.User] = []

        # Custom attributes
        self.can_send_announcement = False
        self.announcements = [
            "Welcome to the server! Please read the rules before chatting.",
            "We have a new plugin! Check it out by typing /plugins.",
            "We have a new feature! Check it out by typing /features.", 
            "We have a new update! Check it out by typing /updates.",
            "Please be respectful to other users."
        ]
        self.ticker_thread = th.Thread(target=self.__ticker)
        self.announcement_thread = th.Thread(target=self.__send_announcement)

    def __ticker(self):
        while True:
            time.sleep(30)
            self.can_send_announcement = True
        
    def __send_announcement(self):
        while True:
            random_announcement = random.choice(self.announcements)
            if self.can_send_announcement:
                SelftosUtils.broadcast(self.prefix, self.online_users, random_announcement, source=None, render_on_console=True, exclude=None)
                self.can_send_announcement = False


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
        if not self.ticker_thread.is_alive():
            self.ticker_thread.start()
        if not self.announcement_thread.is_alive():
            self.announcement_thread.start()

    def on_user_left(self, user: SelftosNetwork.User) -> None:
        """
        Called when a user leaves the server.
        Cancellable: No
        :param user: The user who left the server
        """
        # If the room is empty, stop the ticker and announcement threads
        if len(self.online_users) == 0:
            self.ticker_thread.join()
            self.announcement_thread.join()

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

def PyInit_Announcements():
    return Announcements()
