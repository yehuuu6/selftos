from typing import List
from prompt_toolkit import PromptSession
from rich.markup import escape

import config.loader as SelftosConfig
import utils.functions as SelftosUtils
import classes.network as SelftosNetwork
import socket
import threading
import json
import asyncio
import time

config = SelftosConfig.config

PREFIX = "[magenta]SERVER[/magenta]" # This is a server, not client.
OWNER = config['owner']
PROMPT_PREFIX = f"{config['id']}"

selftos_main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #  Main Server
room_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Room Server Socket
is_running = False # Is the server running?
users_list: List[SelftosNetwork.User] = [] # List of users in the room
input_loop = asyncio.get_event_loop() # Asyncio loop for the admin input

def connect_main_server() -> None:
    """
    Connects to Selftos main server
    """
    MAIN_HOST = "192.168.1.6"
    MAIN_PORT = 7030
    try:
        selftos_main_socket.connect((MAIN_HOST, MAIN_PORT))
    except ConnectionRefusedError:
        SelftosUtils.printf("<CONSOLE> [red]Connection refused by the main server.[/red]")
        exit(1)

def broadcast(msg: str, msg_source: str = PREFIX, render_on_console: bool = False, exclude: SelftosNetwork.User | None = None) -> None:
    """
    Broadcast a message to all the users in the room.
    """
    for user in users_list:
        if msg_source != PREFIX and msg_source == user.name:
            role = user.main_role
            color = user.color
            SelftosUtils.printf(color + role)
            # [[color]role[/color]] 
            perm_indicator = f"[gold3]{escape('[')}[/gold3][{color}]{role}[/{color}][gold3]{escape(']')}[/gold3] "
            break
    else:
        perm_indicator = ""
    
    msg_source = f"[cyan]{msg_source}[/cyan]" if msg_source != PREFIX else msg_source

    msg = f"<{perm_indicator}{msg_source}> {msg}"
    if render_on_console:
        SelftosUtils.printf(msg)
    for user in users_list:
        if user == exclude:
            continue
        package = SelftosNetwork.Package(type = "SFSMessage", content = msg, source = msg_source)
        SelftosNetwork.send_package(package, user.client)

def shutdown(users = users_list, reason: str = "No reason was specified.") -> None:
    """
    Terminates the server with the specified reason.
    """
    global is_running
    broadcast(f"Shutting down! [yellow]({reason})[/yellow]", render_on_console=True)
    for user in users:
        user.disconnect()
    is_running = False
    input_loop.stop()
    users.clear()
    room_socket.close()

################ COMMANDS START ################

def execute_list(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
        SelftosUtils.printc("<CONSOLE> Usage: list <request>", executer)
        SelftosUtils.printc("<CONSOLE> Available requests: users, roles", executer)
        return
    elif args[0] == "users":
        if len(users_list) == 0:
            SelftosUtils.printc("<CONSOLE> [yellow]The room is empty.[/yellow]", executer)
            return
        SelftosUtils.printc("<CONSOLE> Currently online users:", executer)
        for user in users_list:
            index = users_list.index(user) + 1
            SelftosUtils.printc(f"{index} | {user.who()}", executer)
    elif args[0] == "roles":
        SelftosUtils.printc("<CONSOLE> Listing roles:", executer)
        for role in SelftosConfig.config['roles']:
            is_default = role.get('default')
            default_indicator = "[yellow](default)[/yellow]" if is_default else ""
            SelftosUtils.printc(
                f"[bright_magenta]> Name[/bright_magenta]: {role['name']} {default_indicator}:", executer
            )
            SelftosUtils.printc(f"[magenta] - Level[/magenta]: {role['level']}", executer)
            SelftosUtils.printc(f"[bright_magenta] > Permissions[/bright_magenta]:", executer)
            for permission, actions in role['permissions'].items():
                allowed_actions = ", ".join(f"[green]{action}[/green]" for action in actions)
                SelftosUtils.printc(f"[magenta]  - {permission}[/magenta]: {allowed_actions}", executer)

            role_users = role.get('users', [])
            if not role_users:
                SelftosUtils.printc(
                    f"[bright_magenta] > Users[/bright_magenta]: [yellow](empty)[/yellow]", executer
                )
            else:
                SelftosUtils.printc(f"[bright_magenta] > Users[/bright_magenta]:", executer)
                for i, user in enumerate(role_users, start=1):
                    SelftosUtils.printc(f"  - {i} | {user['name']}", executer)

            if role['name'] != SelftosConfig.config['roles'][-1]['name']:
                SelftosUtils.printc("[yellow]----------------------------------------[/yellow]", executer)
                    
    else:
        SelftosUtils.printc("<CONSOLE> [red]Error: You can't list that.[/red]", executer)

def execute_say(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
        SelftosUtils.printc("<CONSOLE> Usage: say <message>", executer)
        return
    msg = " ".join(args)
    broadcast(msg, f"[red3]Console[/red3]", render_on_console=True)

def execute_who(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
            SelftosUtils.printc("<CONSOLE> Usage: who <user_name>", executer)
    else:
        user_name = args[0]
        for user in users_list:
            if user.name == user_name:
                SelftosUtils.printc("<CONSOLE> Detailed user info:", executer)
                SelftosUtils.printc(user.who(detailed=True), executer)
                break
        else:
            SelftosUtils.printc("<CONSOLE> [red]Error: User not found.[/red]", executer)

def execute_kick(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
            SelftosUtils.printc("<CONSOLE> Usage: kick <user_name>", executer)
    else:
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the [red3]Console[/red3]"
        user_name = args[0]
        for user in users_list:
            if user.name == user_name:
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{PREFIX}> You have been [bold red]kicked[/bold red] from the server by {executed_by}.", source = PREFIX)
                SelftosNetwork.send_package(package, user.client)
                user.disconnect()
                broadcast(f"[cyan]{user.name}[/cyan] has been [bold red]kicked[/bold red] from the server by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc("<CONSOLE> [red]Error: User not found.[/red]", executer)

def execute_mute(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) < 2:
        SelftosUtils.printc("<CONSOLE> Usage: mute <user_name> <time_minutes>", executer)
    else:
        user_name = args[0]
        try:
            timeout = int(args[1])
        except ValueError:
            SelftosUtils.printc("<CONSOLE> [red]Error: Invalid timeout value. Must be an integer![/red]", executer)
            return
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the [red3]Console[/red3]"
        for user in users_list:
            if user.name == user_name:
                result = user.mute(timeout)
                if not result:
                    SelftosUtils.printc("<CONSOLE> [red]Error: User is already muted.[/red]", executer)
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{PREFIX}> You have been [red]muted[/red] by {executed_by}.", source = PREFIX)
                SelftosNetwork.send_package(package, user.client)
                broadcast(f"[cyan]{user.name}[/cyan] has been [red]muted[/red] by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc("<CONSOLE> [red]Error: User not found.[/red]", executer)

def execute_unmute(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
            SelftosUtils.printc("<CONSOLE> Usage: unmute <user_name>", executer)
    else:
        user_name = args[0]
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the [red3]Console[/red3]"
        for user in users_list:
            if user.name == user_name:
                result = user.unmute()
                if not result:
                    SelftosUtils.printc("<CONSOLE> [red]Error: User is not muted.[/red]", executer)
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{PREFIX}> You have been [green3]unmuted[/green3] by {executed_by}.", source = PREFIX)
                SelftosNetwork.send_package(package, user.client)
                broadcast(f"[cyan]{user.name}[/cyan] has been [green3]unmuted[/green3] by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc("<CONSOLE> [red]Error: User not found.[/red]", executer)

def execute_op(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
            SelftosUtils.printc("<CONSOLE> Usage: op <user_name>", executer)
    else:
        user_name = args[0]
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the [red3]Console[/red3]"
        for user in users_list:
            if user.name == user_name:
                result = user.op()
                if not result:
                    SelftosUtils.printc("<CONSOLE> [red]Error: User already has operator privileges.[/red]", executer)
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{PREFIX}> Congratulations! You have been granted [red3]operator[/red3] privileges by {executed_by}.", source = PREFIX)
                SelftosNetwork.send_package(package, user.client)
                broadcast(f"[cyan]{user.name}[/cyan] has been granted [red3]operator[/red3] privileges by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc("<CONSOLE> [red]Error: User not found.[/red]", executer)

def execute_deop(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
        SelftosUtils.printc("<CONSOLE> Usage: deop <user_name>", executer)
    else:
        user_name = args[0]
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the [red3]Console[/red3]"
        for user in users_list:
            if user.name == user_name:
                result = user.deop()
                if not result:
                    SelftosUtils.printc("<CONSOLE> [red]Error: User doesn't have operator privileges.[/red]", executer)
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{PREFIX}> Your [red3]operator[/red3] privileges have been [red]revoked[/red] by {executed_by}.", source = PREFIX)
                SelftosNetwork.send_package(package, user.client)
                broadcast(f"[cyan]{user.name}[/cyan] has been revoked [red3]operator[/red3] privileges by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc("<CONSOLE> [red]Error: User not found.[/red]", executer)

def execute_ban(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) < 2:
        SelftosUtils.printc("<CONSOLE> Usage: ban <user_name> <time_hours>", executer)
    else:
        user_name = args[0]
        try:
            timeout = int(args[1])
        except ValueError:
            SelftosUtils.printc("<CONSOLE> [red]Error: Invalid timeout value. Must be an integer![/red]", executer)
            return
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the [red3]Console[/red3]"
        for user in users_list:
            if user.name == user_name:
                result = user.ban(timeout)
                if not result:
                    SelftosUtils.printc("<CONSOLE> [red]Error: User is already banned.[/red]", executer)
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{PREFIX}> You have been [bold red]banned[/bold red] from the server by {executed_by}", source = PREFIX)
                SelftosNetwork.send_package(package, user.client)
                user.disconnect()
                broadcast(f"[cyan]{user.name}[/cyan] has been [bold red]banned[/bold red] from the server by {executed_by}", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc("<CONSOLE> [red]Error: User not found.[/red]", executer)

def execute_unban(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
            SelftosUtils.printc("<CONSOLE> Usage: unban <user_name>", executer)
    else:
        user_name = args[0]
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the [red3]Console[/red3]"
        with open(SelftosNetwork.User.bans_list_path, "r") as bans_file:
            bans = json.load(bans_file)
        for ban in bans:
            if ban["name"] == user_name:
                bans.remove(ban)
                with open(SelftosNetwork.User.bans_list_path, "w") as bans_file:
                    json.dump(bans, bans_file, indent=2)
                broadcast(f"[cyan]{user_name}[/cyan] has been [green3]unbanned[/green3] from the server by {executed_by}", render_on_console=True)
                break
        else:
            SelftosUtils.printc("<CONSOLE> [red]Error: User is not banned.[/red]", executer)

def execute_clear(args: List[str], executer: SelftosNetwork.User | None) -> None:
    SelftosUtils.clear_console()

def execute_grant(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) < 2:
            SelftosUtils.printc("<CONSOLE> Usage: grant <user_name> <role_name>", executer)
            return
    try:
        user_name = str(args[0])
        role_name = str(args[1])
    except ValueError:
        SelftosUtils.printc("<CONSOLE> [red]Error: Invalid argument type. Must be strings![/red]", executer)
        return

    for role in SelftosConfig.config['roles']:
        if role_name == role['name']:
            break
    else:
        SelftosUtils.printc(f"<CONSOLE> [red]Error: Can't find any role named '{role_name}'[/red]", executer)
        return
    executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the [red3]Console[/red3]"
    for user in users_list:
        user.roles = [role for role in user.roles]
        if user.name == user_name:
            if not user.add_role(role_name):
                SelftosUtils.printc(f"<CONSOLE> [red]Error: User already has '{role_name}' role.[/red]", executer)
                return
            SelftosUtils.printc(f"<CONSOLE> [green3]Success! Granted[/green3] [bold yellow]{role_name}[/bold yellow] role to [cyan]{user_name}[/cyan].", executer)
            inform_grant = SelftosNetwork.Package(type = "SFSMessage", content = f"<{PREFIX}> You have been [green3]granted[/green3] [bold yellow]{role_name}[/bold yellow] role by {executed_by}.", source = PREFIX)
            SelftosNetwork.send_package(inform_grant, user.client)
            # Update SelftosConfig.config['roles']
            for role in SelftosConfig.config['roles']:
                if role_name == role['name']:
                    role['users'].append({"name": user_name})
                    break
            break
    else:
        SelftosUtils.printc("<CONSOLE> [red]Error: User not found.[/red]", executer)

def execute_revoke(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) < 2:
            SelftosUtils.printc("<CONSOLE> Usage: revoke <user_name> <role_name>", executer)
            return
    try:
        user_name = str(args[0])
        role_name = str(args[1])
    except ValueError:
        SelftosUtils.printc("<CONSOLE> [red]Error: Invalid argument type. Must be strings![/red]", executer)
        return
    
    for role in SelftosConfig.config['roles']:
        if role_name == role['name']:
            break
    else:
        SelftosUtils.printc(f"<CONSOLE> [red]Error: Can't find any role named '{role_name}'[/red]", executer)
        return
    executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the [red3]Console[/red3]"
    for user in users_list:
        user.roles = [role for role in user.roles]
        if user.name == user_name:
            if not user.remove_role(role_name):
                SelftosUtils.printc(f"<CONSOLE> [red]Error: User is not assigned to '{role_name}' role.[/red]", executer)
                return
            SelftosUtils.printc(f"<CONSOLE> [green3]Success![/green3] [red]Revoked[/red] [bold yellow]{role_name}[/bold yellow] role from [cyan]{user_name}[/cyan]., executer", executer)
            inform_revoke = SelftosNetwork.Package(type = "SFSMessage", content = f"<{PREFIX}> Your [bold yellow]{role_name}[/bold yellow] role has been [red]revoked[/red] by {executed_by}.", source = PREFIX)
            SelftosNetwork.send_package(inform_revoke, user.client)
            # Update SelftosConfig.config['roles']
            for role in SelftosConfig.config['roles']:
                if role_name == role['name']:
                    for user in role['users']:
                        if user['name'] == user_name:
                            role['users'].remove(user)
                            break
                    break
            break
    else:
        SelftosUtils.printc("<CONSOLE> [red]Error: User not found.[/red]", executer)

def execute_help(args: List[str], executer: SelftosNetwork.User | None) -> None:
    help_output = [
        "<CONSOLE> List of commands | [cyan]Arguments marked with * are required[/cyan]",
        f"[magenta]> list[/magenta] [yellow]{escape('[items*]')}[/yellow] - Prints out a list of the specified items.",
        f"[magenta]> say[/magenta] [yellow]{escape('[message*]')}[/yellow] - Broadcast a message to all the users in the room from [italic]console[/italic].",
        f"[magenta]> kick[/magenta] [yellow]{escape('[user*]')}[/yellow] - Kicks the specified user from the server.",
        f"[magenta]> mute[/magenta] [yellow]{escape('[user*]')}[/yellow] - Mutes the specified user.",
        f"[magenta]> unmute[/magenta] [yellow]{escape('[user*]')}[/yellow] - Unmutes the specified user.",
        f"[magenta]> op[/magenta] [yellow]{escape('[user*]')}[/yellow] - Grants operator privileges to the specified user.",
        f"[magenta]> deop[/magenta] [yellow]{escape('[user*]')}[/yellow] - Revokes operator privileges from the specified user.",
        f"[magenta]> grant[/magenta] [yellow]{escape('[user*]')}[/yellow] [yellow]{escape('[role*]')}[/yellow] - Grants the specified role to the specified user.",
        f"[magenta]> revoke[/magenta] [yellow]{escape('[user*]')}[/yellow] [yellow]{escape('[role*]')}[/yellow] - Revokes the specified role from the specified user.",
        f"[magenta]> ban[/magenta] [yellow]{escape('[user*]')}[/yellow] - Bans the specified user from the server.",
        f"[magenta]> unban[/magenta] [yellow]{escape('[user*]')}[/yellow] - Unbans the specified user from the server.",
        f"[magenta]> who[/magenta] [yellow]{escape('[user*]')}[/yellow] - Shows [italic]detailed[/italic] information about the specified user.",
        f"[magenta]> clear[/magenta] - Clears the console.",
        f"[magenta]> shutdown[/magenta] [yellow]{escape('[reason]')}[/yellow] - Closes the server and broadcasts the reason to all the users in the room."
    ]
    package_content = ""
    for line in help_output:
        if executer is not None:
            package_content += f"{line}\n"
        else:
            SelftosUtils.printf(line)
    if executer is not None:
        package = SelftosNetwork.Package(type = "SFSMessage", content = package_content, source = PREFIX)
        SelftosNetwork.send_package(package, executer.client)

COMMANDS = {
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

################ COMMANDS END ################

def package_handler(package: SelftosNetwork.Package, sender: socket.socket) -> None:
    """
    Manages received packages.
    """
    if not package.is_valid_package():
        SelftosUtils.printf("<CONSOLE> Invalid package received, something is wrong!")
        _package = SelftosNetwork.Package(type = "SFSMessage", content = "You have send an invalid package. Connection will be closed.", source = PREFIX)
        SelftosNetwork.send_package(_package, sender)
        sender.close()

    if package.type == "SFSUserData":
        user_data: dict = json.loads(str(package.content))
        user_id = user_data["id"]
        user_name = user_data["name"]

        user = SelftosNetwork.User(id = user_id, name = user_name, client = sender)

        if user.is_banned:
            banned_inform_package = SelftosNetwork.Package(type = "SFSMessage", content = "[red3]You are banned from this room![/red3]", source = PREFIX)
            SelftosNetwork.send_package(banned_inform_package, sender)
            user.disconnect()
            SelftosUtils.printf(f"<CONSOLE> [cyan]{user.name}[/cyan] tried to join the room, but they are [red]banned[/red].")
            return

        users_list.append(user)

        if user.name == OWNER:
            user.is_op = True
            broadcast(f"Attention! an [red3]operator[/red3] is joining to the room.", render_on_console=True)

        broadcast(f"[cyan]{user.name}[/cyan] has joined the room.", render_on_console=True, exclude=user)

    elif package.type == "SFSMessage":
        user = SelftosUtils.get_user_by_socket(sock = sender, users_list = users_list)
        if user is None:
            return
        if user.is_muted:
            muted_inform_package = SelftosNetwork.Package(type = "SFSMessage", content = f"<{PREFIX}> You are muted.", source = PREFIX)
            SelftosNetwork.send_package(muted_inform_package, sender)
            if config['show_muted_messages']:
                SelftosUtils.printf(f"[red]MUTED[/red] | <[cyan]{user.name}[/cyan]> [strike]{escape(str(package.content))}[/strike]")
            return
        broadcast(f"{escape(str(package.content))}", msg_source=f"{user.name}", render_on_console=True)

    elif package.type == "SFSCommand":
        user = SelftosUtils.get_user_by_socket(sock = sender, users_list = users_list)
        if user is None:
            return
        command = str(package.content).strip().split(' ')[0]
        args = str(package.content).strip().split(' ')[1:]
        if not user.has_permission(command, args):
            SelftosNetwork.send_package(SelftosNetwork.Package(type = "SFSMessage", content = f"<CONSOLE> [red]Error: You don't have permission to execute this command.[/red]", source = PREFIX), sender)
            return
        if command == "shutdown":
            if len(args) == 0:
                shutdown()
            else:
                s_msg = " ".join(args)
                shutdown(reason=s_msg)
            return
        requested_command = COMMANDS.get(command)
        if requested_command is None:
            SelftosNetwork.send_package(SelftosNetwork.Package(type = "SFSMessage", content = f"<CONSOLE> Command [red]'{command}'[/red] not found. Type 'help' to list commands.", source = PREFIX), sender)
            return
        else:
            requested_command(args, executer = user)

def client_handler(client: socket.socket, address: tuple) -> None:
    while is_running:
        package = SelftosNetwork.get_package(client)
        if package is not None:
            package_handler(package, client)
        else:
            if is_running:
                SelftosUtils.printf(f"<CONSOLE> Connection from {address} has been lost.")
                user = SelftosUtils.get_user_by_socket(client, users_list)
                if user is not None:
                    users_list.remove(user)
                    broadcast(f"[cyan]{user.name}[/cyan] has left the room.", render_on_console=True)
            break

def connection_handler() -> None:
    while is_running:
        try:
            client_socket, address = room_socket.accept()
            SelftosUtils.printf(f"<CONSOLE> Connection from {address} has been established.")

            client_handler_thread = threading.Thread(target=client_handler, args=(client_socket, address), daemon=True)
            client_handler_thread.start()

            package = SelftosNetwork.Package(type = "SFSHandshake", content = "nickname", source = PREFIX) # TODO: Give server info to the client in content.
            SelftosNetwork.send_package(package, client_socket)

        except socket.error as e:
            if (not is_running):
                break
            else:
                print(f"<[red]ERROR[/red]> Failed to accept connection: {e}")
        except KeyboardInterrupt:
            shutdown()
            break

async def handle_admin_input() -> None:

    session = PromptSession(f"console@{PROMPT_PREFIX}" + r"\~ ", erase_when_done=True)

    while is_running:  
        try:
            cin = await session.prompt_async()
        except (EOFError, KeyboardInterrupt):
            shutdown()
            break

        input_list = cin.strip().split(' ')
        command: str = input_list[0]
        args: List[str] = input_list[1:]

        if command == "shutdown":
            if len(args) == 0:
                shutdown()
            else:
                s_msg = " ".join(args)
                shutdown(reason=s_msg)
        else:
            requested_command = COMMANDS.get(command)
            if requested_command is None:
                SelftosUtils.printf(f"<CONSOLE> Command [red]'{command}'[/red] not found. Type 'help' to list commands.")
                continue
            else:
                requested_command(args, executer = None)

def start() -> None:
    global is_running
    #connect_main_server()
    try:
        room_socket.bind((config['host'], config['port']))
        room_socket.listen(config['maxUsers'])

        is_running = True

        connection_handler_thread = threading.Thread(target=connection_handler, daemon=True)
        connection_handler_thread.start()
    except Exception as e:
        SelftosUtils.printf(f"<CONSOLE> [red]Error: Can not start the server: {e}[/red]")
        exit(1)
    else:
        SelftosUtils.printf(f"<CONSOLE> Server is [green3]online[/green3] and listening on {config['host']}:{config['port']}")
    
def main():
    SelftosUtils.printf("<CONSOLE> Starting the room server...")
    start()
    input_loop.create_task(handle_admin_input())
    input_loop.run_forever()

if __name__ == "__main__":
    main()