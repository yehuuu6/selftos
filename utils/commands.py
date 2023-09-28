"""\
This module provides the necessary admin commands for your Selftos chat application.
Currently, we have to give users list as an argument because if we import it, it won't update the list
and use the old one which is empty from the start. We need to import users list from room.py dynamically.
So it will be the updated version of the list.
"""

import utils.functions as SelftosUtils
import classes.SelftosNetwork as SelftosNetwork

from rich.markup import escape

from typing import List

FILE_TYPE = "[magenta]SERVER[/magenta]"

def broadcast(users: List[SelftosNetwork.User], msg: str, msg_source: str = FILE_TYPE, render_on_server: bool = False, exclude: SelftosNetwork.User | None = None) -> None:
    """
    Broadcast a message to all the users in the room.
    """
    if render_on_server:
        SelftosUtils.printf(f"<{msg_source}> {msg}")
    for user in users:
        if user == exclude:
            continue
        package = SelftosNetwork.Package(type = "SFSMessage", content = msg, source = msg_source)
        SelftosNetwork.send_package(package, user.client)

def execute_list(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
        SelftosUtils.printf("<SERVER> Usage: list <request>")
        return
    elif args[0] == "users":
        if len(users) == 0:
            SelftosUtils.printf("<SERVER> [yellow]The room is empty.[/yellow]")
            return
        SelftosUtils.printf("<SERVER> Users:")
        for user in users:
            SelftosUtils.printf(user.who())
    else:
        SelftosUtils.printf("<[red]ERROR[/red]> [red]You can't list that.[/red]")

def execute_say(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
        SelftosUtils.printf("<SERVER> Usage: say <message>")
        return
    msg = " ".join(args)
    broadcast(users, msg, f"[red3]Admin[/red3]", render_on_server=True)

def execute_who(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<SERVER> Usage: who <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                SelftosUtils.printf(user.who())
                break
        else:
            SelftosUtils.printf("<[red]ERROR[/red]> [red]User not found.[/red]")

def execute_kick(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<SERVER> Usage: kick <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                package = SelftosNetwork.Package(type = "SFSMessage", content = "You have been [bold red]kicked[/bold red] from the room.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                user.kick()
                broadcast(users, f"[cyan]{user.name}[/cyan] has been [bold red]kicked[/bold red] from the room.", render_on_server=True)
                break
        else:
            SelftosUtils.printf("<[red]ERROR[/red]> [red]User not found.[/red]")

def execute_mute(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<SERVER> Usage: mute <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                package = SelftosNetwork.Package(type = "SFSMessage", content = "You have been [red2]muted[/red2] by the admin.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                user.mute()
                broadcast(users, f"[cyan]{user.name}[/cyan] has been [red2]muted[red2] by the admin.", render_on_server=True, exclude=user)
                break
        else:
            SelftosUtils.printf("<[red]ERROR[/red]> [red]User not found.[/red]")

def execute_unmute(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<SERVER> Usage: unmute <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                package = SelftosNetwork.Package(type = "SFSMessage", content = "You have been [green3]unmuted[/green3] by the admin.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                user.unmute()
                broadcast(users, f"[cyan]{user.name}[/cyan] has been [green3]unmuted[/green3] by the admin.", render_on_server=True, exclude=user)
                break
        else:
            SelftosUtils.printf("<[red]ERROR[/red]> [red]User not found.[/red]")

def execute_admin(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<SERVER> Usage: admin <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                package = SelftosNetwork.Package(type = "SFSMessage", content = "Congratulations! You have been granted [red3]admin[/red3] privileges by the server.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                user.admin()
                broadcast(users, f"[cyan]{user.name}[/cyan] has been granted [red3]admin[/red3] privileges by the server.", render_on_server=True, exclude=user)
                break
        else:
            SelftosUtils.printf("<[red]ERROR[/red]> [red]User not found.[/red]")

def execute_unadmin(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
        SelftosUtils.printf("<SERVER> Usage: unadmin <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                package = SelftosNetwork.Package(type = "SFSMessage", content = "You no longer have [red3]admin[/red3] privileges on the server.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                user.unadmin()
                broadcast(users, f"[cyan]{user.name}[/cyan] no longer has [red3]admin[/red3] privileges on the server.", render_on_server=True, exclude=user)
                break
        else:
            SelftosUtils.printf("<[red]ERROR[/red]> [red]User not found.[/red]")

def execute_ban(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<SERVER> Usage: ban <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                package = SelftosNetwork.Package(type = "SFSMessage", content = "You have been [bold red]banned[/bold red] from the room.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                user.ban()
                broadcast(users, f"[cyan]{user.name}[/cyan] has been [bold red]banned[/bold red] from the room.", render_on_server=True)
                break
        else:
            SelftosUtils.printf("<[red]ERROR[/red]> [red]User not found.[/red]")

def execute_clear(users: List[SelftosNetwork.User], args: List[str]) -> None:
    SelftosUtils.clear_console()

def execute_help(users: List[SelftosNetwork.User], args: List[str]) -> None:
    SelftosUtils.printf("<SERVER> List of commands | [blue]Arguments marked with * are required[/blue]");
    SelftosUtils.printf(f"[magenta]~ list[/magenta] [yellow]{escape('[items*]')}[/yellow] - Prints out a list of the specified items.");
    SelftosUtils.printf(f"[magenta]~ say[/magenta] [yellow]{escape('[message*]')}[/yellow] - Broadcasts a message to all the users in the room as admin.");
    SelftosUtils.printf(f"[magenta]~ kick[/magenta] [yellow]{escape('[user*]')}[/yellow] - Kicks the specified user from the room.");
    SelftosUtils.printf(f"[magenta]~ mute[/magenta] [yellow]{escape('[user*]')}[/yellow] - Mutes the specified user.");
    SelftosUtils.printf(f"[magenta]~ unmute[/magenta] [yellow]{escape('[user*]')}[/yellow] - Unmutes the specified user.");
    SelftosUtils.printf(f"[magenta]~ admin[/magenta] [yellow]{escape('[user*]')}[/yellow] - Grants admin privileges to the specified user.");
    SelftosUtils.printf(f"[magenta]~ unadmin[/magenta] [yellow]{escape('[user*]')}[/yellow] - Revokes admin privileges from the specified user.");
    SelftosUtils.printf(f"[magenta]~ ban[/magenta] [yellow]{escape('[user*]')}[/yellow] - Bans the specified user from the room.");
    SelftosUtils.printf(f"[magenta]~ who[/magenta] [yellow]{escape('[user*]')}[/yellow] - Shows information about the specified user.");
    SelftosUtils.printf(f"[magenta]~ clear[/magenta] - [yellow]Clears the console.");
    SelftosUtils.printf(f"[magenta]~ shutdown[/magenta] [yellow]{escape('[reason]')}[/yellow] - Closes the server and broadcasts the reason to all the users in the room.");

COMMANDS = {
    "broadcast": broadcast,
    "list": execute_list,
    "say": execute_say,
    "who": execute_who,
    "kick": execute_kick,
    "mute": execute_mute,
    "unmute": execute_unmute,
    "admin": execute_admin,
    "unadmin": execute_unadmin,
    "ban": execute_ban,
    "clear": execute_clear,
    "help": execute_help
}