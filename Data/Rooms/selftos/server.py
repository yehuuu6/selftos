import socket
from threading import Thread
import time
import pymysql
import sys
from colorama import Fore, Back, Style, init

init(autoreset=True)

try:
    conn = pymysql.connect(host="localhost", user="root", password="", db="selftos")
    myCursor = conn.cursor()
except:
    print("Connection failed to database.")
    time.sleep(3)
    exit()


def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s connected." % client_address)
        client.send(
            bytes("8jhhaZaaq766712h5aaoaoaoaoppp17127477VVVAHAGgagx0Pz_12", "utf8")
        )
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):
    while True:
        t = time.localtime()
        current_time = time.strftime("[%H:%M:%S]", t)
        Thread(target=announcements, args=(client,)).start()
        try:
            name = client.recv(BUFSIZ).decode("utf8")
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
            except:
                pass
            try:
                users.remove(name)
            except:
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

            elif msg == "7AHSGHA8125125125.AGSAGMKJASAH_1571257125AHSH.ZZZZZ":
                client.send(
                    bytes("[Room] Failed to send message, try again...", "utf8")
                )

            elif checkMessage.find("kagsjhHYA") != -1:
                sender = checkMessage.split("+")[1]
                filename = checkMessage.split("+")[2]
                newFile = (
                    "jkkasgjasg76666AJHAHAHxxxxCf"
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

        except:
            try:
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

        if msg != "1J731JSG81jags881952kdpiSf18shj-123aasgxXAGa11_sfgCCCXXzzzz":
            msglog = msg.decode("utf8").rstrip()
            namelog = name

            message_log = current_time + " " + namelog + ": " + msglog
            with open("LOGS.txt", "a") as output:
                output.write(message_log + "\n")


def announcements(client):
    while True:
        try:
            time.sleep(120)
            timeoutProtect = (
                "1J731JSG81jags881952kdpiSf18shj-123aasgxXAGa11_sfgCCCXXzzzz"
            )
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


with open("roomName.txt", "r") as f:
    roomName = f.readline().strip()

sql = "SELECT * FROM rooms WHERE name = %s"
num_row = myCursor.execute(sql, roomName)
result_set = myCursor.fetchone()
portstr = result_set[2]

HOST = "192.168.1.9"
PORT = int(portstr)
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
SERVER.bind((ADDR))

if __name__ == "__main__":
    SERVER.listen(5)
    print(Fore.GREEN + "Server Started!")
    print(Fore.GREEN + "Clients now can connect.")
    print(Fore.GREEN + "Listening on port " + str(portstr) + "\n")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
