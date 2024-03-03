"""\
This module provides the necessary functions for your Selftos chat application.
"""

from typing import List

import library.network as SelftosNetwork
import socket

def clear_console() -> None: ...

def get_current_time() -> str: ...

def printf(msg: str) -> None: ...

def printc(messages: List[str], executer: SelftosNetwork.User | None) -> None: ...

def get_user_by_socket(sock: socket.socket, users_list: List[SelftosNetwork.User]) -> SelftosNetwork.User | None: ...

def broadcast(prefix: str, users: List[SelftosNetwork.User], message: str, source: str | None = None, render_on_console: bool = False, exclude: SelftosNetwork.User | None = None) -> None: ...