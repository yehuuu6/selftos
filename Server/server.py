import socket
from threading import Thread
import time
import os
from xmlrpc.client import Server
import pymysql
from colorama import Fore, Back, Style, init

init(autoreset=True)

if not os.path.exists("config.txt"):
    print(Fore.RED + "Can't find config file. Creating one...")
    with open("config.txt", "w") as f:
        f.writelines("token \nname ExampleServer\nbind 127.0.0.1\nport 7030")
    f.close()
    print(Fore.GREEN + "Config file created! Please set important values.")
    exit()

try:
    conn = pymysql.connect(host="localhost", user="root", password="", db="selftos")
    myCursor = conn.cursor()
except Exception as e:
    print("Connection failed to database. Error: " + e)
    time.sleep(3)
    exit()


def GetConfig():
    global ServerToken
    global ServerName
    global ServerPassword
    global ServerBind
    global ServerPort
    global ServerOwner

    ServerPassword = ""

    with open("config.txt") as f:
        lines = f.readlines()
    for line in lines:
        line = line.split()
        try:
            if line[0].lower() == "token":
                ServerToken = line[1]
                print(Fore.YELLOW + "Room token set to " + ServerToken)
            if line[0].lower() == "name":
                ServerName = line[1]
                print(Fore.YELLOW + "Room name set to " + ServerName)
            if line[0].lower() == "bind":
                ServerBind = line[1]
                print(Fore.YELLOW + "Server IP set to " + ServerBind)
            if line[0].lower() == "password":
                ServerPassword = line[1]
                print(Fore.YELLOW + "Room Password set to " + ServerPassword)
            if line[0].lower() == "port":
                ServerPort = line[1]
                print(Fore.YELLOW + "Server port set to " + ServerPort)
            if line[0].lower() == "owner":
                ServerOwner = line[1]
                print(Fore.YELLOW + "Room owner set to " + ServerOwner)
        except IndexError:
            print(
                "Please set important values in the config file.\ntoken: Unique room token given by selftos.com\nname: Your rooms name\nport: Server port value\nbind: Server IP address"
            )
            exit()
    f.close()

    if ServerPassword == "":
        print(Fore.RED + "-IMPORTANT- Room has no password protection!")


def accept_incoming_connections():
    global client_address
    while True:
        try:
            client, client_address = SERVER.accept()
            client.send(bytes("$SELFTOSe553dadb4d1a48f1bf2cb130f4834cb7", "utf8"))
            addresses[client] = client_address
            Thread(target=handle_client, args=(client,)).start()
        except KeyboardInterrupt:
            SERVER.close()
            exit()


def handle_client(client):
    name = client.recv(BUFSIZ).decode("utf8")
    print("User " + name + " (%s:%s) connected." % client_address)
    while True:
        t = time.localtime()
        current_time = time.strftime("[%H:%M:%S]", t)
        Thread(target=announcements, args=(client,)).start()
        try:
            if name in users:
                client.send(
                    bytes("Looks like you're already connected to the server!", "utf8")
                )
                try:
                    del clients[client]
                except KeyError:
                    raise KeyError("[ERROR 100] " + name + " Multiple Client Try.")
            else:
                users.append(name)
                global usernames
                usernames = ", ".join(users)
                welcome = "[Room] Welcome " + name + ". Enjoy!" + "+"
                tmp = " "
                tmp = tmp.join(list(clients.values()))
                welcome = welcome + tmp
                client.send(bytes(welcome, "utf8"))
                clients[client] = name
                msg = name + " connected to room." + "+"
                joinlog = (
                    current_time + " >>>>>" + name + " connected to room." + "<<<<<"
                )
                with open("LOGS.txt", "a") as output:
                    output.write(joinlog + "\n")
                output.close()
                tmp = " "
                tmp = tmp.join(list(clients.values()))
                msg = msg + tmp
                broadcast(bytes(msg, "utf8"))
                break
        except ConnectionResetError:
            try:
                del clients[client]
            except Exception:
                pass
            try:
                users.remove(name)
            except Exception:
                pass

        except BrokenPipeError:
            pass
    while True:
        try:
            msg = client.recv(BUFSIZ)
            checkMessage = str(msg)
            if len(msg) > 60:
                client.send(
                    bytes(
                        "[Room] Message is too long (maximum is 60 characters).", "utf8"
                    )
                )

            elif checkMessage.find("kagsjhHYA") != -1:
                sender = checkMessage.split("+")[1]
                filename = checkMessage.split("+")[2]
                newFile = (
                    "$SELFTOS26487d04a6884dc1a1bfd6607816554d"
                    + "+"
                    + "[Room] "
                    + sender
                    + " has sent '"
                    + filename
                    + "."
                )
                broadcast(bytes(newFile, "utf8"))

            else:
                broadcast(msg, name + ": ")

        except Exception:
            try:
                print("User " + name + " (%s:%s) disconnected." % client_address)
                client.close()
                users.remove(name)
                del clients[client]
                msg = name + " left the chat." + "+"
                leftlog = current_time + " >>>>>" + name + " left the chat." + "<<<<<"
                with open("LOGS.txt", "a") as output:
                    output.write(leftlog + "\n")
                output.close()
                msg = msg + name
                broadcast(bytes(msg, "utf8"))
                break
            except KeyError:
                break

        if msg != "$SELFTOScd82e9a9f5f74794b201f1081f482dad":
            msglog = msg.decode("utf8").rstrip()
            namelog = name

            message_log = current_time + " " + namelog + ": " + msglog
            with open("LOGS.txt", "a") as output:
                output.write(message_log + "\n")


def announcements(client):
    while True:
        try:
            time.sleep(120)
            timeoutProtect = "$SELFTOScd82e9a9f5f74794b201f1081f482dad"
            client.send(bytes(timeoutProtect, "utf8"))
            time.sleep(120)
        except OSError:
            pass


def broadcast(msg, prefix=""):
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


users = []
clients = {}
addresses = {}

print(Fore.YELLOW + "Getting config...")
GetConfig()

HOST = ServerBind
PORT = int(ServerPort)
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
SERVER.bind((ADDR))

if __name__ == "__main__":
    SERVER.listen(5)

    PortCheck = "SELECT * FROM rooms WHERE token = %s"
    myCursor.execute(PortCheck, ServerToken)
    results = myCursor.fetchone()
    cIP = results[5]
    cPass = results[3]
    cName = results[2]
    cPort = results[4]
    cOwner = results[6]
    if str(cName) != str(ServerName):
        print(
            f"New room name ({str(ServerName)}) found. Updating the old one ({str(cName)})..."
        )
        values = (ServerName, ServerToken)
        sql = "UPDATE rooms SET name=%s WHERE token = %s"
        myCursor.execute(sql, values)
        conn.commit()
    if str(cPass) != str(ServerPassword):
        print(
            f"New room password ({str(ServerPassword)}) found. Updating the old one ({str(cPass)})..."
        )
        values = (ServerPassword, ServerToken)
        sql = "UPDATE rooms SET password=%s WHERE token = %s"
        myCursor.execute(sql, values)
        conn.commit()
    if str(cName) != str(ServerName):
        print(
            f"New room name ({str(ServerName)}) found. Updating the old one ({str(cName)})..."
        )
        values = (ServerName, ServerToken)
        sql = "UPDATE rooms SET name=%s WHERE token = %s"
        myCursor.execute(sql, values)
        conn.commit()
    if str(cIP) != str(ServerBind):
        print(
            f"New IP address ({str(ServerBind)}) found. Updating the old one ({str(cIP)})..."
        )
        values = (ServerBind, ServerToken)
        sql = "UPDATE rooms SET ip=%s WHERE token = %s"
        myCursor.execute(sql, values)
        conn.commit()
    if str(cPort) != str(ServerPort):
        print(
            f"New port value ({str(ServerPort)}) found. Updating the old one ({str(cPort)})..."
        )
        values = (ServerPort, ServerToken)
        sql = "UPDATE rooms SET port=%s WHERE token = %s"
        myCursor.execute(sql, values)
        conn.commit()
    if str(cOwner) != str(ServerOwner):
        print(
            f"New owner ({str(ServerOwner)}) found. Updating the old one ({str(cOwner)})..."
        )
        values = (ServerOwner, ServerToken)
        sql = "UPDATE rooms SET owner=%s WHERE token = %s"
        myCursor.execute(sql, values)
        conn.commit()

    print(Fore.GREEN + "Users now can connect to the room.")
    print(Fore.GREEN + "Listening on port " + str(ServerPort) + "\n")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
