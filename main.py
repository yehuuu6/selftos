import paramiko
import pymysql
from socket import AF_INET, socket, SOCK_STREAM
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5 import uic
import sys
from threading import Thread
import time
import secrets
from config.constants import *
import webbrowser
import Sources.icons.icons_rc


class Selftos:
    def __init__(self, version):
        super(Selftos, self).__init__()
        self.version = version

    def ConnectMain(self):
        try:
            global conn
            global myCursor
            conn = pymysql.connect(
                host="localhost", user="root", password="", db="selftos"
            )
            myCursor = conn.cursor()
            global client
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ipofssh, username=nicknamessh, password=password)
            global transport
            global sftp
            transport = client.get_transport()
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp = client.open_sftp()
        except Exception as e:
            print("Failed to connect: " + str(e))

    def CheckRoom(self, RoomName, RoomToken):
        try:
            sftp = client.open_sftp()
        except:
            print("Check your internet connection...")

        myCursor.execute("SELECT * FROM data")
        result_set = myCursor.fetchone()
        vers = result_set[1]

        if vers != self.version:
            print(
                "New update available! To continue to use this program,\ndownload new version."
            )
        else:
            sql = "SELECT * FROM rooms WHERE name = %s"
            num_row = myCursor.execute(sql, RoomName)
            result_set = myCursor.fetchone()
            if num_row < 1:
                print("Can't find room.")
            else:
                nameRoom = result_set[2]
                tokenRoom = result_set[3]
                port = result_set[4]
                host = result_set[5]
                global owner
                owner = result_set[6]
                if nameRoom == RoomName and tokenRoom == RoomToken:

                    def disconnect():
                        client_socket.close()
                        CWindow.usrList.clear()
                        CWindow.msgList.clear()
                        CWindow.hide()
                        LWindow.show()

                    def receive():
                        while True:
                            t = time.localtime()
                            current_time = time.strftime("[%H:%M]", t)
                            try:
                                msg = client_socket.recv(BUFSIZ).decode("utf8")
                                if msg == "$SELFTOSe553dadb4d1a48f1bf2cb130f4834cb7":
                                    client_socket.send(usernameofuser.encode("utf8"))

                                elif (
                                    msg.find("$SELFTOS26487d04a6884dc1a1bfd6607816554d")
                                    != -1
                                ):
                                    gizliKod = msg.split("+")[0]
                                    sentFile = msg.split("+")[1]
                                    CWindow.msgList.addItem(sentFile)

                                elif msg.find("connected to room.") != -1:
                                    msg_to_print = msg.split("+")[0]
                                    online_users = msg.split("+")[1]
                                    CWindow.usrList.takeItem(0)

                                    for user in online_users.split(" "):
                                        checkUsr = CWindow.usrList.findItems(
                                            user, Qt.MatchExactly
                                        )

                                        if len(checkUsr) < 1:
                                            CWindow.usrList.addItem(user)
                                            if user == result_set[6]:
                                                checkOwner = CWindow.usrList.findItems(
                                                    user, Qt.MatchExactly
                                                )
                                                for i in checkOwner:
                                                    i.setForeground(
                                                        QBrush(QColor("#fcba03"))
                                                    )

                                    CWindow.msgList.addItem("[Room] " + msg_to_print)

                                elif msg.find("left the chat.") != -1:
                                    msg_to_print = msg.split("+")[0]
                                    userr = msg.split("+")[1]
                                    CWindow.msgList.addItem("[Room] " + msg_to_print)
                                    idx = CWindow.usrList.findItems(
                                        userr, Qt.MatchExactly
                                    )

                                    for item in idx:
                                        item.setHidden(True)
                                elif (
                                    msg.find("$SELFTOScd82e9a9f5f74794b201f1081f482dad")
                                    != -1
                                ):
                                    pass
                                elif msg.find("Welcome") != -1:
                                    try:
                                        msg_to_print = msg.split("+")[0]
                                        online_users = msg.split("+")[1]
                                        for user in online_users.split(" "):
                                            CWindow.usrList.addItem(user)
                                        CWindow.msgList.addItem(msg_to_print)
                                    except IndexError:
                                        pass
                                else:
                                    CWindow.msgList.addItem(current_time + " " + msg)
                            except OSError:
                                break

                    def send(event=None):
                        try:
                            msg = CWindow.msgBox.text()
                            CWindow.msgBox.setText("")
                            client_socket.send(bytes(msg, "utf8"))
                        except OSError:
                            pass

                    BUFSIZ = 4096
                    ADDR = (host, port)

                    def ConnectRoom():
                        global client_socket
                        client_socket = socket(AF_INET, SOCK_STREAM)
                        client_socket.connect(ADDR)

                    try:
                        ConnectRoom()
                    except:
                        print("Room server is offline.")
                    else:
                        receive_thread = Thread(target=receive)
                        CWindow.enableChat(nameRoom)
                        CWindow.sendBtn.clicked.connect(send)
                        CWindow.msgBox.returnPressed.connect(send)
                        CWindow.disconnectBtn.clicked.connect(disconnect)
                        receive_thread.start()

                else:
                    print("Wrong credentials.")

    def Register(self):
        webbrowser.open("https://store.planetofplugins.ml/gateway/register/")

    def Login(self):
        global usernameofuser
        usernameofuser = "K4NeX"
        passwordofuser = "1234"
        sql = "SELECT * FROM users WHERE username = %s"
        num_row = myCursor.execute(sql, usernameofuser)
        result_set = myCursor.fetchone()

        """if num_row < 1:
			print("Can't find any user...")		
		else:"""
        # passwordchecking = result_set[11]
        passwordchecking = "1234"
        try:
            if passwordofuser == passwordchecking:
                token = secrets.token_hex(32)
                values = (token, usernameofuser)
                tokenCreation = "UPDATE users SET token=%s WHERE username = %s"
                myCursor.execute(tokenCreation, values)
                conn.commit()
                print("Logged in!")
                LWindow.username.setText(usernameofuser)
            else:
                print("Login failed...")
        except UnboundLocalError:
            pass


class ChatWindow(QMainWindow):
    def __init__(self):
        super(ChatWindow, self).__init__()
        uic.loadUi("Sources/uis/chat_gui.ui", self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(f"Selftos LWindow {SelftosController.version}")
        self.setWindowIcon(QIcon(":/icons/icons/github.svg"))
        self.disconnectBtn = self.findChild(QPushButton, "disconnectButton_3")
        self.msgList = self.findChild(QListWidget, "msgPage")
        self.roomName = self.findChild(QLabel, "label_14")
        self.closeButton = self.findChild(QPushButton, "close_window_button_3")
        self.maximizeButton = self.findChild(QPushButton, "restore_window_button_3")
        self.minimizeButton = self.findChild(QPushButton, "minimize_window_button_3")
        self.sizeGrip = self.findChild(QFrame, "size_grip_3")
        self.Header1 = self.findChild(QFrame, "Header_4")
        self.Header2 = self.findChild(QFrame, "Header_5")
        self.closeButton.clicked.connect(self.exitApp)
        self.maximizeButton.clicked.connect(self.maximizeApp)
        self.roomName = self.findChild(QLabel, "label_14")
        self.usrList = self.findChild(QListWidget, "ActiveUserList")
        self.minimizeButton.clicked.connect(self.showMinimized)
        self.msgBox = self.findChild(QLineEdit, "msgBox")
        self.sendBtn = self.findChild(QPushButton, "sendBtn")
        QSizeGrip(self.sizeGrip)
        self.usrList = self.findChild(QListWidget, "ActiveUserList")

        def moveWindow(e):
            if not self.isMaximized():
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()

        self.Header1.mouseMoveEvent = moveWindow
        self.Header2.mouseMoveEvent = moveWindow

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def exitApp(self):
        self.close()
        try:
            client_socket.close()
        except:
            pass

    def maximizeApp(self):
        if self.isMaximized():
            self.showNormal()
            self.maximizeButton.setIcon(QIcon(":/icons/icons/maximize-2.svg"))
        else:
            self.showMaximized()
            self.maximizeButton.setIcon(QIcon(":/icons/icons/minimize-2.svg"))

    def enableChat(self, name):
        self.show()
        self.setWindowTitle(f"{name} - Selftos Active Chat Room")
        self.roomName.setText(f"Chat Room: {name}")
        LWindow.hide()


class LauncherWindow(QMainWindow):
    def __init__(self):
        super(LauncherWindow, self).__init__()
        uic.loadUi("Sources/uis/interface.ui", self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.setWindowTitle(f"Selftos LWindow {SelftosController.version}")
        self.shadow.setBlurRadius(50)
        self.shadow.setXOffset(0)
        self.username = self.findChild(QLabel, "username")
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 92, 157, 550))
        self.centralwidget.setGraphicsEffect(self.shadow)
        self.setWindowIcon(QIcon(":/icons/icons/github.svg"))
        self.connectBtn = self.findChild(QPushButton, "connectButton")
        self.roomNameIn = self.findChild(QLineEdit, "roomName")
        self.roomTokenIn = self.findChild(QLineEdit, "roomToken")
        self.closeButton = self.findChild(QPushButton, "close_window_button")
        self.maximizeButton = self.findChild(QPushButton, "restore_window_button")
        self.minimizeButton = self.findChild(QPushButton, "minimize_window_button")
        self.sizeGrip = self.findChild(QFrame, "size_grip")
        self.Header = self.findChild(QFrame, "Header")
        self.closeButton.clicked.connect(self.exitApp)
        self.maximizeButton.clicked.connect(self.maximizeApp)
        self.minimizeButton.clicked.connect(self.showMinimized)
        self.connectBtn.clicked.connect(
            lambda: SelftosController.CheckRoom(
                LWindow.roomNameIn.text(), LWindow.roomTokenIn.text()
            )
        )

        QSizeGrip(self.sizeGrip)

        def moveWindow(e):
            if not self.isMaximized():
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()

        self.Header.mouseMoveEvent = moveWindow
        self.show()

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def exitApp(self):
        self.close()

    def maximizeApp(self):
        if self.isMaximized():
            self.showNormal()
            self.maximizeButton.setIcon(QIcon(":/icons/icons/maximize-2.svg"))
        else:
            self.showMaximized()
            self.maximizeButton.setIcon(QIcon(":/icons/icons/minimize-2.svg"))


StartApp = QApplication(sys.argv)

SelftosController = Selftos("5.0.0")

LWindow = LauncherWindow()
CWindow = ChatWindow()

SelftosController.ConnectMain()
SelftosController.Login()

StartApp.exec_()
