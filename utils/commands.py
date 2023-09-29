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

def broadcast(users: List[SelftosNetwork.User], msg: str, msg_source: str = FILE_TYPE, render_on_console: bool = False, exclude: SelftosNetwork.User | None = None) -> None:
    """
    Broadcast a message to all the users in the room.
    """
    msg = f"<[cyan]{msg_source}[/cyan]> {msg}"
    if render_on_console:
        SelftosUtils.printf(msg)
    for user in users:
        if user == exclude:
            continue
        package = SelftosNetwork.Package(type = "SFSMessage", content = msg, source = msg_source)
        SelftosNetwork.send_package(package, user.client)

def execute_list(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
        SelftosUtils.printf("<CONSOLE> Usage: list <request>")
        return
    elif args[0] == "users":
        if len(users) == 0:
            SelftosUtils.printf("<CONSOLE> [yellow]The room is empty.[/yellow]")
            return
        SelftosUtils.printf("<CONSOLE> Currently online users:")
        for user in users:
            index = users.index(user) + 1
            SelftosUtils.printf(f"{index} | {user.who()}")
    else:
        SelftosUtils.printf("<CONSOLE> [red]Error: You can't list that.[/red]")

def execute_say(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
        SelftosUtils.printf("<CONSOLE> Usage: say <message>")
        return
    msg = " ".join(args)
    broadcast(users, msg, f"[red3]Console[/red3]", render_on_console=True)

def execute_who(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<CONSOLE> Usage: who <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                SelftosUtils.printf("<CONSOLE> User info:")
                SelftosUtils.printf(user.who())
                break
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User not found.[/red]")

def execute_kick(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<CONSOLE> Usage: kick <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> You have been [bold red]kicked[/bold red] from the server by the console.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                user.disconnect()
                broadcast(users, f"[cyan]{user.name}[/cyan] has been [bold red]kicked[/bold red] from the server by the console.", render_on_console=True)
                break
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User not found.[/red]")

def execute_mute(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<CONSOLE> Usage: mute <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                result = user.mute()
                if not result:
                    SelftosUtils.printf("<CONSOLE> [red]Error: User is already muted.[/red]")
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> You have been [red]muted[/red] by the console.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                broadcast(users, f"[cyan]{user.name}[/cyan] has been [red2]muted[red2] by the console.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User not found.[/red]")

def execute_unmute(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<CONSOLE> Usage: unmute <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                result = user.unmute()
                if not result:
                    SelftosUtils.printf("<CONSOLE> [red]Error: User is not muted.[/red]")
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> You have been [green3]unmuted[/green3] by the console.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                broadcast(users, f"[cyan]{user.name}[/cyan] has been [green3]unmuted[/green3] by the console.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User not found.[/red]")

def execute_admin(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<CONSOLE> Usage: admin <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                result = user.admin()
                if not result:
                    SelftosUtils.printf("<CONSOLE> [red]Error: User already has admin privileges.[/red]")
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> Congratulations! You have been granted [red3]admin[/red3] privileges by the console.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                broadcast(users, f"[cyan]{user.name}[/cyan] has been granted [red3]admin[/red3] privileges by the console.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User not found.[/red]")

def execute_unadmin(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
        SelftosUtils.printf("<CONSOLE> Usage: unadmin <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                result = user.unadmin()
                if not result:
                    SelftosUtils.printf("<CONSOLE> [red]Error: User doesn't have admin privileges.[/red]")
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> Your [red3]Admin[/red3] privileges have been revoked by the console.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                broadcast(users, f"[cyan]{user.name}[/cyan] has been revoked [red3]Admin[/red3] privileges by the console.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User not found.[/red]")

def execute_ban(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<CONSOLE> Usage: ban <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                result = user.ban()
                if not result:
                    SelftosUtils.printf("<CONSOLE> [red]Error: User is already banned.[/red]")
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> You have been [bold red]banned[/bold red] from the server by the console", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                user.disconnect()
                broadcast(users, f"[cyan]{user.name}[/cyan] has been [bold red]banned[/bold red] from the server by the console", render_on_console=True)
                break
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User not found.[/red]")

def execute_unban(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<CONSOLE> Usage: unban <user_name>")
    else:
        user_name = args[0]
        with open(SelftosNetwork.User.bans_list_path, "r") as bans_list:
            bans = [ban.strip() for ban in bans_list.readlines()]
        for ban in bans:
            if ban == user_name:
                bans.remove(ban)
                with open(SelftosNetwork.User.bans_list_path, "w") as bans_list:
                    for ban in bans:
                        bans_list.write(ban + '\n')
                broadcast(users, f"[cyan]{user_name}[/cyan] has been [green3]unbanned[/green3] from the server by the console", render_on_console=True)
                return
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User is not banned.[/red]")

def execute_clear(users: List[SelftosNetwork.User], args: List[str]) -> None:
    SelftosUtils.clear_console()

def execute_help(users: List[SelftosNetwork.User], args: List[str]) -> None:
    SelftosUtils.printf("<CONSOLE> List of commands | [cyan]Arguments marked with * are required[/cyan]");
    SelftosUtils.printf(f"[magenta]> list[/magenta] [yellow]{escape('[items*]')}[/yellow] - Prints out a list of the specified items.");
    SelftosUtils.printf(f"[magenta]> say[/magenta] [yellow]{escape('[message*]')}[/yellow] - Broadcasts a message to all the users in the room as the [italic]console[/italic].");
    SelftosUtils.printf(f"[magenta]> kick[/magenta] [yellow]{escape('[user*]')}[/yellow] - Kicks the specified user from the server.");
    SelftosUtils.printf(f"[magenta]> mute[/magenta] [yellow]{escape('[user*]')}[/yellow] - Mutes the specified user.");
    SelftosUtils.printf(f"[magenta]> unmute[/magenta] [yellow]{escape('[user*]')}[/yellow] - Unmutes the specified user.");
    SelftosUtils.printf(f"[magenta]> admin[/magenta] [yellow]{escape('[user*]')}[/yellow] - Grants admin privileges to the specified user.");
    SelftosUtils.printf(f"[magenta]> unadmin[/magenta] [yellow]{escape('[user*]')}[/yellow] - Revokes admin privileges from the specified user.");
    SelftosUtils.printf(f"[magenta]> ban[/magenta] [yellow]{escape('[user*]')}[/yellow] - Bans the specified user from the server.");
    SelftosUtils.printf(f"[magenta]> unban[/magenta] [yellow]{escape('[user*]')}[/yellow] - Unbans the specified user from the server.");
    SelftosUtils.printf(f"[magenta]> who[/magenta] [yellow]{escape('[user*]')}[/yellow] - Shows information about the specified user.");
    SelftosUtils.printf(f"[magenta]> clear[/magenta] - [yellow]Clears the console.");
    SelftosUtils.printf(f"[magenta]> shutdown[/magenta] [yellow]{escape('[reason]')}[/yellow] - Closes the server and broadcasts the reason to all the users in the room.");

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
    "unban": execute_unban,
    "clear": execute_clear,
    "help": execute_help
}