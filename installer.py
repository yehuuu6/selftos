from ast import Return
from re import T
import paramiko
import os, winshell
import time
from win32com.client import Dispatch
from Config.constants import *
import ctypes
import math

appdata = os.getenv("APPDATA")
desktop = winshell.desktop()
ctypes.windll.kernel32.SetConsoleTitleW("Selftos Installer")

iconp = sshmainpath+"/setico.ico"
serverVer = sshmainpath+"/Server_Data/version.txt"
localVer = appdata+"/Selftos/version.txt"
imgp = sshmainpath+"/setup.png"
gop = sshmainpath+"/gobutton.png"
localgop = appdata+"/Selftos/download.png"
localiconp = appdata+"/Selftos/icon.ico"
localimgp = appdata+"/Selftos/img.png"

def Download():

    print("Downloading files...")

    try:
        localaiconp = appdata+"/Selftos/Sources/icon.ico"
        localfile1 = appdata+"/Selftos/Sources/settings.png"
        localfile2 = appdata+"/Selftos/Sources/download.png"
        localfile3 = appdata+"/Selftos/Sources/upload.png"
        localimgp = appdata+"/Selftos/Sources/img.png"
        locallinkp = appdata+"/Selftos/Sources/linkbutton.png"
        localexep = appdata+"/Selftos/Selftos.exe"
        servericonp = sshmainpath+"/App/Sources/icon.ico"
        settingspath = sshmainpath+"/App/Sources/settings.png"
        downloadpath1 = sshmainpath+"/App/Sources/download.png"
        serverlinkp = sshmainpath+"/App/Sources/linkbutton.png"
        serverlupload = sshmainpath+"/App/Sources/upload.png"
        serverimgp = sshmainpath+"/App/Sources/img.png"
        mainexe = sshmainpath+"/App/Selftos.exe"

        progressDict={}
        progressEveryPercent=10

        for i in range(0,101):
            if i%progressEveryPercent==0:
                progressDict[str(i)]=""
        

        def ProgressBar(x, y, app):

            bar_len = 50
            filled_len = math.ceil(bar_len * x / float(y))
            percents = math.ceil(100.0 * x / float(y))
            bar = '█' * filled_len + '▁' * (bar_len - filled_len)
            filesize = f'{math.ceil(y/1024):,} KB' if y > 1024 else f'{y} byte'
            print(f'{bar} {percents}% {filesize} {app}\r', end="", flush=True)

        sftp = client.open_sftp()
        sftp.get(mainexe, localexep, callback=lambda x,y: ProgressBar(x,y,mainexe))
        sftp.get(serverimgp, localimgp, callback=lambda x,y: ProgressBar(x,y,serverimgp))
        sftp.get(servericonp, localaiconp, callback=lambda x,y: ProgressBar(x,y,servericonp))
        sftp.get(serverlupload, localfile3, callback=lambda x,y: ProgressBar(x,y,serverlupload))
        sftp.get(downloadpath1, localfile2, callback=lambda x,y: ProgressBar(x,y,downloadpath1))
        sftp.get(serverlinkp, locallinkp, callback=lambda x,y: ProgressBar(x,y,serverlinkp))
        sftp.get(settingspath, localfile1, callback=lambda x,y: ProgressBar(x,y,settingspath))
        sftp.close()

        print("\nDownloaded files! Now creating shortcut...")
        path = os.path.join(desktop, "Selftos.lnk")
        target = appdata+"/Selftos/Selftos.exe"
        wDir = appdata+"/Selftos/"
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.save()
    except:
        print("Something went wrong... Try again later.")
    else:
        print("Done!")
        try:
            os.remove(appdata+"/Selftos/icon.ico")
            os.remove(appdata+"/Selftos/download.png")
            os.remove(appdata+"/Selftos/img.png")
        except:
            pass
        exit()

try:
    print("Trying to connect to main server...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ipofssh, username=nicknamessh, password=password)
    transport = client.get_transport()
except:
    print("Connection failed, program terminating...")
    time.sleep(3)
    exit()

print("Connected to the server!")
print("Checking local files...")

try:
    os.mkdir (appdata+"/Selftos")
    os.mkdir(appdata+"/Selftos/Sources/")
    print("Created local files!")
    isUser = False
except OSError:
    print("Found local files!")
    isUser = True
    pass

if (isUser == False):

    print("Type 'download' to download Selftos (without quotes).")

else:
    print("Type 'reinstall' to reinstall your Selftos installation to fix issues. Or type 'update' to update if available (without quotes).")

while True:
    req = input("Selftos>")
    if(req == "download" or req == "reinstall"):
        Download()
    elif (req == "exit"):
        print("Installation canceled by user. Program terminating...")
        time.sleep(1)
        exit()
    else:
        print("Unknown command. Type 'exit' to terminate program (without quotes).")
