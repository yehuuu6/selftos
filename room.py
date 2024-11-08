from typing import List
from prompt_toolkit import PromptSession, ANSI
from rich.markup import escape
from loaders.plugin_loader import PluginLoader
from loaders.config_loader import ConfigLoader
from time import sleep

import utils.functions as SelftosUtils
import library.network as SelftosNetwork
import socket as sck
import threading
import json
import asyncio

PREFIX = f"<[magenta]Console[/magenta]>"

# Initialize the loader objects
config_loader = ConfigLoader()
plugin_loader = PluginLoader()

# Load the configuration
SelftosUtils.printf(f"{PREFIX} Starting configuration loader...")
config = config_loader.load()

OWNER = config['owner']
PROMPT_PREFIX = f"{config['id']}"

selftos_main_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM) #  Main Server
room_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM) # Room Server Socket
is_running = False # Is the server running?
users_list: List[SelftosNetwork.User] = [] # List of users in the room

def connect_main_server() -> None:
    """
    Connects to Selftos main server
    """
    MAIN_HOST = "192.168.1.6"
    MAIN_PORT = 7030
    try:
        selftos_main_socket.connect((MAIN_HOST, MAIN_PORT))
    except ConnectionRefusedError:
        SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Connection refused by the main server.")
        sleep(3)
        exit(1)

def shutdown(reason: str = "No reason was specified.") -> None:
    """
    Terminates the server with the specified reason.
    """
    global is_running
    SelftosUtils.broadcast(prefix=PREFIX, users=users_list, message=f"Shutting down! [bold yellow]({reason})[/bold yellow]", render_on_console=True)
    for user in users_list:
        user.disconnect()
    is_running = False
    global input_loop
    input_loop.stop()
    users_list.clear()
    room_socket.close()

################ COMMANDS START ################

def execute_list(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
        output_a = [
            f"{PREFIX} Usage: list <request>",
            f"[magenta]> Available requests:[/magenta] [bold yellow]users, roles, plugins[/bold yellow]"
        ]
        SelftosUtils.printc(output_a, executer)
        return
    elif args[0] == "users":
        if len(users_list) == 0:
            SelftosUtils.printc([f"{PREFIX} [orange1]Warning:[/orange1] The room is empty."], executer)
            return
        output_b = [f"{PREFIX} Currently online users:"]
        for user in users_list:
            index = users_list.index(user) + 1
            output_b.append(f"{index} | {user.who()}")
        SelftosUtils.printc(output_b, executer)
    elif args[0] == "roles":
        output_c = [f"{PREFIX} Listing roles:"]
        for role in config['roles']:
            index = config['roles'].index(role) + 1
            is_default = role.get('default')
            default_indicator = f"[bold yellow](default)[/bold yellow]" if is_default else ""
            output_c.append(f"[magenta] {index}. Role[/magenta]: [{role['color']}]{role['name']}[/{role['color']}] {default_indicator}")
            output_c.append(f"[magenta] - Level[/magenta]: {role['level']}")
            output_c.append(f"[magenta] > Permissions[/magenta]:")
            for permission, actions in role['permissions'].items():
                allowed_actions = ", ".join(f"[green]{action}[/green]" for action in actions)
                output_c.append(f"[magenta]  - {permission}[/magenta]: {allowed_actions}")

            role_users = role.get('users', [])
            if not is_default:
                if not role_users:
                    output_c.append(f"[magenta] > Users[/magenta]: [bold yellow](empty)[/bold yellow]")
                else:
                    output_c.append(f"[magenta] > Users[/magenta]:")
                    for i, user in enumerate(role_users, start=1):
                        output_c.append(f"  - {i} | {user['name']}")
            else:
                output_c.append(f"[magenta] > Users[/magenta]: [bold yellow](everyone)[/bold yellow]")

            if role['name'] != config['roles'][-1]['name']:
                output_c.append(f"[bold yellow]----------------------------------------[/bold yellow]")
        SelftosUtils.printc(output_c, executer)

    elif args[0] == "plugins":
        if len(plugin_loader.plugins) == 0:
            SelftosUtils.printc([f"{PREFIX} [orange1]Warning:[/orange1] No plugins loaded."], executer)
            return
        output_d = [f"{PREFIX} Listing plugins:"]
        for plugin in plugin_loader.plugins:
            num = plugin_loader.plugins.index(plugin) + 1
            output_d.append(f"[magenta] {num}) [blue]{plugin.name} {plugin.version}[/blue][/magenta]")
            output_d.append(f"[magenta]   - [bold yellow]Description[/bold yellow]: {plugin.description}[/magenta]")
            output_d.append(f"[magenta]   - [bold yellow]Author[/bold yellow]: {plugin.author}[/magenta]")
            if plugin != plugin_loader.plugins[-1]:
                output_d.append(f"\n[bold yellow]----------------------------------------[/bold yellow]")
        SelftosUtils.printc(output_d, executer)

    else:
        SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] You can't list that."], executer)

def execute_say(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
        SelftosUtils.printc([f"{PREFIX} Usage: say <message>"], executer)
        return
    msg = " ".join(args)
    SelftosUtils.broadcast(PREFIX, users_list, msg, f"[gold3]{escape('[')}[/gold3][red]Console[/red][gold3]{escape(']')}[/gold3]", render_on_console=True)

def execute_who(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
            SelftosUtils.printc([f"{PREFIX} Usage: who <user_name>"], executer)
    else:
        user_name = args[0]
        for user in users_list:
            if user.name == user_name:
                SelftosUtils.printc([f"{PREFIX} Detailed user info:"], executer)
                SelftosUtils.printc([f"{user.who(detailed=True)}"], executer)
                break
        else:
            SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User not found."], executer)

def execute_kick(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
            SelftosUtils.printc([f"{PREFIX} Usage: kick <user_name>"], executer)
    else:
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the Console"
        user_name = args[0]
        for user in users_list:
            if user.name == user_name:
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} You have been kicked from the server by {executed_by}.")
                SelftosNetwork.send_package(package, user.sock)
                user.disconnect()
                SelftosUtils.broadcast(PREFIX, users_list, f"[cyan]{user.name}[/cyan] has been kicked from the server by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User not found."], executer)

def execute_mute(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) < 1:
        SelftosUtils.printc([f"{PREFIX} Usage: mute <user_name>"], executer)
    else:
        user_name = args[0]
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the Console"
        for user in users_list:
            if user.name == user_name:
                result = user.mute()
                if not result:
                    SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User is already muted."], executer)
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} You have been muted by {executed_by}.")
                SelftosNetwork.send_package(package, user.sock)
                SelftosUtils.broadcast(PREFIX, users_list, f"[cyan]{user.name}[/cyan] has been muted by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User not found."], executer)

def execute_unmute(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
            SelftosUtils.printc([f"{PREFIX} Usage: unmute <user_name>"], executer)
    else:
        user_name = args[0]
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the Console"
        for user in users_list:
            if user.name == user_name:
                result = user.unmute()
                if not result:
                    SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User is not muted."], executer)
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} You have been unmuted by {executed_by}.")
                SelftosNetwork.send_package(package, user.sock)
                SelftosUtils.broadcast(PREFIX, users_list, f"[cyan]{user.name}[/cyan] has been unmuted by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User not found."], executer)

def execute_op(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
            SelftosUtils.printc([f"{PREFIX} Usage: op <user_name>"], executer)
    else:
        user_name = args[0]
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the Console"
        for user in users_list:
            if user.name == user_name:
                result = user.op()
                if not result:
                    SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User already has operator privileges."], executer)
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} You have been granted operator privileges by {executed_by}.")
                SelftosNetwork.send_package(package, user.sock)
                SelftosUtils.broadcast(PREFIX, users_list, f"[cyan]{user.name}[/cyan] has been granted operator privileges by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User not found."], executer)

def execute_deop(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
        SelftosUtils.printc([f"{PREFIX} Usage: deop <user_name>"], executer)
    else:
        user_name = args[0]
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the Console"
        for user in users_list:
            if user.name == user_name:
                result = user.deop()
                if not result:
                    SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User doesn't have operator privileges."], executer)
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} Your operator privileges have been [red]revoked[/red] by {executed_by}.")
                SelftosNetwork.send_package(package, user.sock)
                SelftosUtils.broadcast(PREFIX, users_list, f"[cyan]{user.name}[/cyan] has been revoked operator privileges by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User not found."], executer)

def execute_ban(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) < 1:
        SelftosUtils.printc([f"{PREFIX} Usage: ban <user_name>"], executer)
    else:
        user_name = args[0]
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the Console"
        for user in users_list:
            if user.name == user_name:
                result = user.ban()
                if not result:
                    SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User is already banned."], executer)
                    return
                package = SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} You have been banned from the server by {executed_by}")
                SelftosNetwork.send_package(package, user.sock)
                user.disconnect()
                SelftosUtils.broadcast(PREFIX, users_list, f"[cyan]{user.name}[/cyan] has been banned from the server by {executed_by}.", render_on_console=True, exclude=user)
                break
        else:
            SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User not found."], executer)

def execute_unban(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
            SelftosUtils.printc([f"{PREFIX} Usage: unban <user_name>"], executer)
    else:
        user_name = args[0]
        executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the Console"
        with open(SelftosNetwork.User.bans_list_path, "r") as bans_file:
            bans = json.load(bans_file)
        for ban in bans:
            if ban["name"] == user_name:
                bans.remove(ban)
                with open(SelftosNetwork.User.bans_list_path, "w") as bans_file:
                    json.dump(bans, bans_file, indent=2)
                SelftosUtils.broadcast(PREFIX, users_list, f"[cyan]{user_name}[/cyan] has been unbanned from the server by {executed_by}", render_on_console=True)
                break
        else:
            SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User is not banned."], executer)

def execute_clear(args: List[str], executer: SelftosNetwork.User | None) -> None:
    SelftosUtils.clear_console()

def execute_grant(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) < 2:
            SelftosUtils.printc([f"{PREFIX} Usage: grant <user_name> <role_name>"], executer)
            return
    try:
        user_name = str(args[0])
        role_name = str(args[1])
    except ValueError:
        SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] Invalid argument type. Must be strings!"], executer)
        return

    for role in config['roles']:
        if role_name == role['name']:
            break
    else:
        SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] Can't find any role named '{role_name}'"], executer)
        return
    executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the Console"
    for user in users_list:
        user.roles = [role for role in user.roles]
        if user.name == user_name:
            if not user.add_role(role_name):
                SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User already has '{role_name}' role."], executer)
                return
            SelftosUtils.printc([f"{PREFIX} [green3]Success:[/green3] Granted [bold yellow]{role_name}[/bold yellow] role to {user_name}."], executer)
            inform_grant = SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} You have been granted [bold yellow]{role_name}[/bold yellow] role by {executed_by}.")
            SelftosNetwork.send_package(inform_grant, user.sock)
            # Update config['roles']
            for role in config['roles']:
                if role_name == role['name']:
                    role['users'].append({"name": user_name})
                    break
            break
    else:
        SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User not found."], executer)

def execute_revoke(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) < 2:
            SelftosUtils.printc([f"{PREFIX} Usage: revoke <user_name> <role_name>"], executer)
            return
    try:
        user_name = str(args[0])
        role_name = str(args[1])
    except ValueError:
        SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] Invalid argument type. Must be strings!"], executer)
        return
    
    for role in config['roles']:
        if role_name == role['name']:
            break
    else:
        SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] Can't find any role named '{role_name}'"], executer)
        return
    executed_by = f"[cyan]{executer.name}[/cyan]" if executer is not None else "the Console"
    for user in users_list:
        user.roles = [role for role in user.roles]
        if user.name == user_name:
            if not user.remove_role(role_name):
                SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User is not assigned to '{role_name}' role."], executer)
                return
            SelftosUtils.printc([f"{PREFIX} [green3]Success:[/green3] Revoked [bold yellow]{role_name}[/bold yellow] role from {user_name}."], executer)
            inform_revoke = SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} Your [bold yellow]{role_name}[/bold yellow] role has been revoked by {executed_by}.")
            SelftosNetwork.send_package(inform_revoke, user.sock)
            # Update config['roles']
            for role in config['roles']:
                if role_name == role['name']:
                    for user in role['users']:
                        if user['name'] == user_name:
                            role['users'].remove(user)
                            break
                    break
            break
    else:
        SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] User not found."], executer)

def execute_unload(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
        output_a = [
            f"{PREFIX} Usage: unload <plugin_name>"
        ]
        SelftosUtils.printc(output_a, executer)
        return
    elif len(args) > 0:
        plugin_name = args[0]
        result = plugin_loader.unload_plugin(plugin_name)
        if executer is not None:
            if result:
                SelftosUtils.printc([f"{PREFIX} [green3]Success:[/green3] Plugin [blue]{plugin_name}[/blue] has been unloaded."], executer)
            else:
                SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] Plugin [blue]{plugin_name}[/blue] not found."], executer)

def execute_reload(args: List[str], executer: SelftosNetwork.User | None) -> None:
    if len(args) == 0:
        output_a = [
            f"{PREFIX} Usage: reload <request>",
            f"[magenta]> Available requests:[/magenta] [bold yellow]plugins[/bold yellow]"
        ]
        SelftosUtils.printc(output_a, executer)
        return
    elif args[0] == "plugins":
        result = plugin_loader.reload_plugins(users_list)
        if result:
            SelftosUtils.printc([f"{PREFIX} [green3]Success:[/green3] Plugins reloaded."], executer)
    else:
        SelftosUtils.printc([f"{PREFIX} [red]Error:[/red] You can't reload that."], executer)

def execute_help(args: List[str], executer: SelftosNetwork.User | None) -> None:
    help_output = [
        f"{PREFIX} List of commands | [cyan]Arguments marked with * are required[/cyan]",
        f"[magenta]> list[/magenta] [bold yellow]{escape('[items*]')}[/bold yellow] - Prints out a list of the specified items.",
        f"[magenta]> say[/magenta] [bold yellow]{escape('[message*]')}[/bold yellow] - Broadcast a message to all the users in the room from [italic]console[/italic].",
        f"[magenta]> kick[/magenta] [bold yellow]{escape('[user*]')}[/bold yellow] - Kicks the specified user from the server.",
        f"[magenta]> mute[/magenta] [bold yellow]{escape('[user*]')}[/bold yellow] - Mutes the specified user.",
        f"[magenta]> unmute[/magenta] [bold yellow]{escape('[user*]')}[/bold yellow] - Unmutes the specified user.",
        f"[magenta]> op[/magenta] [bold yellow]{escape('[user*]')}[/bold yellow] - Grants operator privileges to the specified user.",
        f"[magenta]> deop[/magenta] [bold yellow]{escape('[user*]')}[/bold yellow] - Revokes operator privileges from the specified user.",
        f"[magenta]> grant[/magenta] [bold yellow]{escape('[user*]')}[/bold yellow] [bold yellow]{escape('[role*]')}[/bold yellow] - Grants the specified role to the specified user.",
        f"[magenta]> revoke[/magenta] [bold yellow]{escape('[user*]')}[/bold yellow] [bold yellow]{escape('[role*]')}[/bold yellow] - Revokes the specified role from the specified user.",
        f"[magenta]> ban[/magenta] [bold yellow]{escape('[user*]')}[/bold yellow] - Bans the specified user from the server.",
        f"[magenta]> unban[/magenta] [bold yellow]{escape('[user*]')}[/bold yellow] - Unbans the specified user from the server.",
        f"[magenta]> who[/magenta] [bold yellow]{escape('[user*]')}[/bold yellow] - Shows [italic]detailed[/italic] information about the specified user.",
        f"[magenta]> clear[/magenta] - Clears the console.",
        f"[magenta]> reload[/magenta] [bold yellow]{escape('[request*]')}[/bold yellow] - Reloads the specified systems.",
        f"[magenta]> unload[/magenta] [bold yellow]{escape('[plugin*]')}[/bold yellow] - Unloads the specified plugin.",
        f"[magenta]> shutdown[/magenta] [bold yellow]{escape('[reason]')}[/bold yellow] - Closes the server and broadcasts the reason to all the users in the room."
    ]
    SelftosUtils.printc(help_output, executer)

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
        "reload" : execute_reload,
        "unload" : execute_unload,
        "help": execute_help
    }

################ COMMANDS END ################

def package_handler(package: SelftosNetwork.Package, sender: sck.socket) -> None:
    """
    Manages received packages.
    """

    if not package.is_valid_package():
        SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Invalid package received, something is wrong!")
        _package = SelftosNetwork.Package(type = "SFSMessage", content = "You have send an invalid package. Connection will be closed.")
        SelftosNetwork.send_package(_package, sender)
        sender.close()

    if package.type == "SFSUserData":
        user_data: dict = json.loads(str(package.content))
        user_id = user_data["id"]
        user_name = user_data["name"]

        user = SelftosNetwork.User(id = user_id, name = user_name, sock = sender)

        if user.is_banned:
            banned_inform_package = SelftosNetwork.Package(type = "SFSMessage", content = "You are banned from this room!")
            SelftosNetwork.send_package(banned_inform_package, sender)
            user.disconnect()
            SelftosUtils.printf(f"{PREFIX} [cyan]{user.name}[/cyan] tried to join the room, but they are banned.")
            return

        users_list.append(user)
        if user.name == OWNER['name']:
            user.is_op = True
            SelftosUtils.broadcast(PREFIX, users_list, f"Attention! Owner [cyan]{user.name}[/cyan] has joined the room.", render_on_console=True)

        SelftosUtils.broadcast(PREFIX, users_list, f"[cyan]{user.name}[/cyan] has joined the room.", render_on_console=True, exclude=user)

        for plugin in plugin_loader.plugins:
            try:
                plugin.online_users = users_list
                plugin.on_user_joined(user)
            except Exception as e:
                SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Plugin '{plugin.name}' has failed to handle user join event. Cause: {e}")

    elif package.type == "SFSMessage":
        user = SelftosUtils.get_user_by_socket(sock = sender, users_list = users_list)
        if user is None:
            return
        if package.content == "":
            return
        # If package content has only spaces, ignore it.
        if SelftosUtils.is_space(package.content):
            return
        if user.is_muted:
            muted_inform_package = SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} You are muted.")
            SelftosNetwork.send_package(muted_inform_package, sender)
            if config['show_muted_messages']:
                SelftosUtils.printf(f"[red]MUTED[/red] | [cyan]{user.name}[/cyan] [strike]{escape(str(package.content))}[/strike]")
            return

        for plugin in plugin_loader.plugins:
            try:
                broadcast_authorization = plugin.on_message_received(user, package.content)
                # If the plugin returns something other than True or False, it's invalid.
                if not isinstance(broadcast_authorization, bool):
                    SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Plugin [blue]{plugin.name}[/blue] has returned an invalid value. It must be a boolean. Shutting down the server.")
                    shutdown(f"'{plugin.name}' is an invalid plugin. Remove it and start the server.")
                    return
            except Exception as e:
                SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Plugin '{plugin.name}' has failed to handle message event. Cause: {e}")
            else:
                if not broadcast_authorization:
                    SelftosUtils.printf(f"{PREFIX} [orange1]Warning:[/orange1] Plugin '{plugin.name}' cancelled the broadcast event.")
                    return

        SelftosUtils.broadcast(PREFIX, users_list, f"{escape(str(package.content))}", source=f"{user.name}", render_on_console=True)

    elif package.type == "SFSCommand":
        user = SelftosUtils.get_user_by_socket(sock = sender, users_list = users_list)
        if user is None:
            return
        command = str(package.content).strip().split(' ')[0]
        args = str(package.content).strip().split(' ')[1:]

        for plugin in plugin_loader.plugins:
            try:
                execute_authorization = plugin.on_command_executed(user, command, args)
                if not isinstance(execute_authorization, bool):
                    SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Plugin [blue]{plugin.name}[/blue] has returned an invalid value. It must be a boolean. Shutting down the server.")
                    shutdown(f"'{plugin.name}' is an invalid plugin. Remove it and start the server.")
                    return
            except Exception as e:
                SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Plugin '{plugin.name}' has failed to handle command event. Cause: {e}")
            else:
                if not execute_authorization:
                    SelftosUtils.printf(f"{PREFIX} [orange1]Warning:[/orange1] Plugin '{plugin.name}' cancelled the command event.")
                    return

        if not user.has_permission(command, args):
            SelftosNetwork.send_package(SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} [red]Error:[/red] You don't have permission to execute this command."), sender)
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
            SelftosNetwork.send_package(SelftosNetwork.Package(type = "SFSMessage", content = f"{PREFIX} Command [red]'{command}'[/red] not found. Type 'help' to list commands."), sender)
            return
        else:
            if config['show_executed_commands']:
                SelftosUtils.printf(f"{PREFIX} [cyan]{user.name}[/cyan] executed command: [bold yellow]{command} {args}[/bold yellow]")
            requested_command(args, executer = user)

def client_handler(client: sck.socket, address: tuple) -> None:
    while is_running:
        package = SelftosNetwork.get_package(client)
        if package is not None:
            for plugin in plugin_loader.plugins:
                try:
                    package_authorization = plugin.on_package_received(client, package)
                    if not isinstance(package_authorization, bool):
                        SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Plugin [blue]{plugin.name}[/blue] has returned an invalid value. It must be a boolean. Shutting down the server.")
                        shutdown(f"'{plugin.name}' is an invalid plugin. Remove it and start the server.")
                        return
                except Exception as e:
                    SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Plugin '{plugin.name}' has failed to handle package event. Cause: {e}")
                else:
                    if not package_authorization:
                        SelftosUtils.printf(f"{PREFIX} [orange1]Warning:[/orange1] Plugin '{plugin.name}' cancelled the package handle event.")
                        return
            package_handler(package, client)
        else:
            if is_running:
                SelftosUtils.printf(f"{PREFIX} Connection from {address} has been lost.")
                user = SelftosUtils.get_user_by_socket(client, users_list)
                if user is not None:
                    users_list.remove(user)
                    SelftosUtils.broadcast(PREFIX, users_list, f"[cyan]{user.name}[/cyan] has left the room.", render_on_console=True)
                    for plugin in plugin_loader.plugins:
                        try:
                            plugin.online_users = users_list
                            plugin.on_user_left(user)
                        except Exception as e:
                            SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Plugin '{plugin.name}' has failed to handle user left event. Cause: {e}")
            break

def connection_handler() -> None:
    while is_running:
        try:
            client_socket, address = room_socket.accept()
            SelftosUtils.printf(f"{PREFIX} Connection from {address} has been established.")

            client_handler_thread = threading.Thread(target=client_handler, args=(client_socket, address), daemon=True)
            client_handler_thread.start()

            package = SelftosNetwork.Package(type = "SFSHandshake", content = "nickname") # TODO: Give server info to the client in content.
            SelftosNetwork.send_package(package, client_socket)

        except sck.error as e:
            if (not is_running):
                break
            else:
                print(f"[red]Error:[/red] Failed to accept connection: {e}")
        except KeyboardInterrupt:
            shutdown()
            break

async def handle_admin_input() -> None:
    prompt_text = f"console@{PROMPT_PREFIX}" + r"\~ "
    session = PromptSession(ANSI(prompt_text), erase_when_done=True)

    while is_running:  
        try:
            cin = await session.prompt_async()
            if cin == "" or SelftosUtils.is_space(cin):
                continue
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
                SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Command '{command}' not found. Type 'help' to list commands.")
                continue
            else:
                requested_command(args, executer = None)

def start() -> None:
    if config['enable_plugins']:
        SelftosUtils.printf(f"{PREFIX} Starting plugin loader...")
        plugin_loader.load_plugins()
    else:
        SelftosUtils.printf(f"{PREFIX} [orange1]Warning:[/orange1] Plugins are disabled in the configuration file.")
    SelftosUtils.printf(f"{PREFIX} Starting the server...")
    global is_running
    #connect_main_server()
    try:
        room_socket.bind((config['host'], config['port']))
        room_socket.listen(config['maxUsers'])

        is_running = True

        connection_handler_thread = threading.Thread(target=connection_handler, daemon=True)
        connection_handler_thread.start()
    except Exception as e:
        SelftosUtils.printf(f"{PREFIX} [red]Error:[/red] Can not start the server: {e}")
        sleep(3)
        exit(1)
    else:
        SelftosUtils.printf(f"{PREFIX} Server is online and listening on {config['host']}:{config['port']}")
    
def main():
    global input_loop
    input_loop = asyncio.new_event_loop()  # Create a new event loop
    asyncio.set_event_loop(input_loop)  # Set it as the current event loop
    start()
    input_loop.create_task(handle_admin_input())
    input_loop.run_forever()

if __name__ == "__main__":
    main()