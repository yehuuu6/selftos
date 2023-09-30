"""\
This module provides the necessary admin commands for your Selftos chat application.
Known Problems:
1- Currently, we have to give users list as an argument because if we import it, it won't update the list
and use the old one which is empty from the start. We need to import users list from room.py dynamically.
So it will be the updated version of the list.
2- We can not send data to the users when they are banned or kicked, because they get disconnected before the message is fully sent.
3- Grant and revoke functions does not work properly. Also we have to dynamically import the config file aswell because
it gets updates from this code but does not affect the config object that room.py uses.
"""

import utils.functions as SelftosUtils
import classes.network as SelftosNetwork
import json
import config.loader as SelftosConfig

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
        SelftosUtils.printf("<CONSOLE> Available requests: users, roles")
        return
    elif args[0] == "users":
        if len(users) == 0:
            SelftosUtils.printf("<CONSOLE> [yellow]The room is empty.[/yellow]")
            return
        SelftosUtils.printf("<CONSOLE> Currently online users:")
        for user in users:
            index = users.index(user) + 1
            SelftosUtils.printf(f"{index} | {user.who()}")
    elif args[0] == "roles":
        SelftosUtils.printf("<CONSOLE> Currently active roles:")
        for role in SelftosConfig.config['roles']:
            is_default = role.get('default')
            if is_default:
                SelftosUtils.printf(f"[bright_magenta]> Name[/bright_magenta]: {role['name']} [yellow](default)[/yellow]:")
            else:
                SelftosUtils.printf(f"[bright_magenta]> Name[/bright_magenta]: {role['name']}:")
            SelftosUtils.printf(f"[magenta] - Level[/magenta]: {role['level']}")
            SelftosUtils.printf(f"[bright_magenta] > Permissions[/bright_magenta]:")
            for permission in role['permissions']:
                allowed = []
                for action in role['permissions'][permission]:
                    allowed.append(f"[green]{action}[/green]")
                SelftosUtils.printf(f"[magenta]  - {permission}[/magenta]: {', '.join(allowed)}")
            if role.get('users') != None:
                if len(role['users']) == 0:
                    SelftosUtils.printf(f"[bright_magenta] > Users[/bright_magenta]: [yellow](empty)[/yellow]")
                    continue
                SelftosUtils.printf(f"[bright_magenta] > Users[/bright_magenta]: ")
                for user in role['users']:
                    i = role['users'].index(user) + 1
                    SelftosUtils.printf(f"  - {i} | {user['name']}")
            SelftosUtils.printf(f"[yellow]----------------------------------------[/yellow]")
                    
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
                SelftosUtils.printf("<CONSOLE> Detailed user info:")
                SelftosUtils.printf(user.who(detailed=True))
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
    if len(args) < 2:
        SelftosUtils.printf("<CONSOLE> Usage: mute <user_name> <time_minutes>")
    else:
        user_name = args[0]
        try:
            timeout = int(args[1])
        except ValueError:
            SelftosUtils.printf("<CONSOLE> [red]Error: Invalid timeout value. Must be an integer![/red]")
            return
        for user in users:
            if user.name == user_name:
                result = user.mute(timeout)
                if not result:
                    SelftosUtils.printf("<CONSOLE> [red]Error: User is already muted.[/red]")
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> You have been [red]muted[/red] by the console.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                broadcast(users, f"[cyan]{user.name}[/cyan] has been [red]muted[red] by the console.", render_on_console=True, exclude=user)
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

def execute_op(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
            SelftosUtils.printf("<CONSOLE> Usage: op <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                result = user.op()
                if not result:
                    SelftosUtils.printf("<CONSOLE> [red]Error: User already has operator privileges.[/red]")
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> Congratulations! You have been granted [red3]operator[/red3] privileges by the console.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                broadcast(users, f"[cyan]{user.name}[/cyan] has been granted [red3]operator[/red3] privileges by the console.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User not found.[/red]")

def execute_deop(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) == 0:
        SelftosUtils.printf("<CONSOLE> Usage: deop <user_name>")
    else:
        user_name = args[0]
        for user in users:
            if user.name == user_name:
                result = user.deop()
                if not result:
                    SelftosUtils.printf("<CONSOLE> [red]Error: User doesn't have operator privileges.[/red]")
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> Your [red3]operator[/red3] privileges have been revoked by the console.", source = FILE_TYPE)
                SelftosNetwork.send_package(package, user.client)
                broadcast(users, f"[cyan]{user.name}[/cyan] has been revoked [red3]operator[/red3] privileges by the console.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User not found.[/red]")

def execute_ban(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) < 2:
        SelftosUtils.printf("<CONSOLE> Usage: ban <user_name> <time_hours>")
    else:
        user_name = args[0]
        try:
            timeout = int(args[1])
        except ValueError:
            SelftosUtils.printf("<CONSOLE> [red]Error: Invalid timeout value. Must be an integer![/red]")
            return
        for user in users:
            if user.name == user_name:
                result = user.ban(timeout)
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
        with open(SelftosNetwork.User.bans_list_path, "r") as bans_file:
            bans = json.load(bans_file)
        for ban in bans:
            if ban["name"] == user_name:
                bans.remove(ban)
                with open(SelftosNetwork.User.bans_list_path, "w") as bans_file:
                    json.dump(bans, bans_file, indent=2)
                broadcast(users, f"[cyan]{user_name}[/cyan] has been [green3]unbanned[/green3] from the server by the console", render_on_console=True)
                break
        else:
            SelftosUtils.printf("<CONSOLE> [red]Error: User is not banned.[/red]")

def execute_clear(users: List[SelftosNetwork.User], args: List[str]) -> None:
    SelftosUtils.clear_console()

def execute_grant(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) < 2:
            SelftosUtils.printf("<CONSOLE> Usage: grant <user_name> <role_name>")
            return
    try:
        user_name = str(args[0])
        role_name = str(args[1])
    except ValueError:
        SelftosUtils.printf("<CONSOLE> [red]Error: Invalid argument type. Must be strings![/red]")
        return

    for user in users:
        user.roles = [role.lower() for role in user.roles]
        if user.name == user_name:
            action = user.add_role(role_name)
            if not action:
                SelftosUtils.printf(f"<CONSOLE> [red]Error:[/red] User already has the role.")
                return
            SelftosUtils.printf(f"<CONSOLE> [green3]Success![/green3] Granted [bold yellow]{role_name}[/bold yellow] to [cyan]{user_name}[/cyan].")
            inform_grant = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> You have been granted [bold yellow]{role_name}[/bold yellow] by the console.", source = FILE_TYPE)
            SelftosNetwork.send_package(inform_grant, user.client)
            break

def execute_revoke(users: List[SelftosNetwork.User], args: List[str]) -> None:
    if len(args) < 2:
            SelftosUtils.printf("<CONSOLE> Usage: revoke <user_name> <role_name>")
            return
    try:
        user_name = str(args[0])
        role_name = str(args[1])
    except ValueError:
        SelftosUtils.printf("<CONSOLE> [red]Error: Invalid argument type. Must be strings![/red]")
        return
    
    for user in users:
        user.roles = [role.lower() for role in user.roles]
        if user.name == user_name:
            action = user.remove_role(role_name)
            if not action:
                SelftosUtils.printf(f"<CONSOLE> [red]Error:[/red] User doesn't have the role.")
                return
            SelftosUtils.printf(f"<CONSOLE> [green3]Success![/green3] Revoked [bold yellow]{role_name}[/bold yellow] from [cyan]{user_name}[/cyan].")
            inform_revoke = SelftosNetwork.Package(type = "SFSMessage", content = f"<{FILE_TYPE}> Your [bold yellow]{role_name}[/bold yellow] role has been revoked by the console.", source = FILE_TYPE)
            SelftosNetwork.send_package(inform_revoke, user.client)
            break

def execute_help(users: List[SelftosNetwork.User], args: List[str]) -> None:
    SelftosUtils.printf("<CONSOLE> List of commands | [cyan]Arguments marked with * are required[/cyan]");
    SelftosUtils.printf(f"[magenta]> list[/magenta] [yellow]{escape('[items*]')}[/yellow] - Prints out a list of the specified items.");
    SelftosUtils.printf(f"[magenta]> say[/magenta] [yellow]{escape('[message*]')}[/yellow] - Broadcast a message to all the users in the room from [italic]console[/italic].");
    SelftosUtils.printf(f"[magenta]> kick[/magenta] [yellow]{escape('[user*]')}[/yellow] - Kicks the specified user from the server.");
    SelftosUtils.printf(f"[magenta]> mute[/magenta] [yellow]{escape('[user*]')}[/yellow] - Mutes the specified user.");
    SelftosUtils.printf(f"[magenta]> unmute[/magenta] [yellow]{escape('[user*]')}[/yellow] - Unmutes the specified user.");
    SelftosUtils.printf(f"[magenta]> op[/magenta] [yellow]{escape('[user*]')}[/yellow] - Grants operator privileges to the specified user.");
    SelftosUtils.printf(f"[magenta]> deop[/magenta] [yellow]{escape('[user*]')}[/yellow] - Revokes operator privileges from the specified user.");
    SelftosUtils.printf(f"[magenta]> ban[/magenta] [yellow]{escape('[user*]')}[/yellow] - Bans the specified user from the server.");
    SelftosUtils.printf(f"[magenta]> unban[/magenta] [yellow]{escape('[user*]')}[/yellow] - Unbans the specified user from the server.");
    SelftosUtils.printf(f"[magenta]> who[/magenta] [yellow]{escape('[user*]')}[/yellow] - Shows [italic]detailed[/italic] information about the specified user.");
    SelftosUtils.printf(f"[magenta]> clear[/magenta] - [yellow]Clears the console.");
    SelftosUtils.printf(f"[magenta]> shutdown[/magenta] [yellow]{escape('[reason]')}[/yellow] - Closes the server and broadcasts the reason to all the users in the room.");

COMMANDS = {
    "broadcast": broadcast,
    "list": execute_list,
    "say": execute_say,
    "who": execute_who,
    "kick": execute_kick,
    "grant": execute_grant,
    "revoke": execute_revoke,
    "mute": execute_mute,
    "unmute": execute_unmute,
    "op": execute_op,
    "deop": execute_deop,
    "ban": execute_ban,
    "unban": execute_unban,
    "clear": execute_clear,
    "help": execute_help
}