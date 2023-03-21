"""
IS496: Computer Networks (Spring 2022)
Programming Assignment 2
Name and netid of each member:
Member 1: jcarte39
Member 2: mkhala6
Member 3: mmaka4
"""

# Import any necessary libraries below
import socket
import sys
import os

BUFFER = 4096


def part1():
    print("********** PART 1 **********")
    host = 'student00.ischool.illinois.edu'
    PORT = 41014
    sin = (host, PORT)

    # Create a datagram socket for TCP
    try:
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.error as e:
        print('Failed to create socket.')
        sys.exit()

    # Bind the socket to address
    try:
        opt = 1
        tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt)
        tcp_server_socket.bind(sin)
    except socket.error as e:
        print('Failed to bind socket.')
        sys.exit()

    # Start listening
    try:
        tcp_server_socket.listen()
        print("Waiting for connection...")
    except socket.error as e:
        print("Failed to wait for connection.")
        sys.exit()

    # Accept the connection and record the address of the client socket
    try:
        connection, address = tcp_server_socket.accept()
    except socket.error as e:
        print("Failed to accept the connection.")
        sys.exit()

    # Receive message from the client
    try:
        message_bytes = connection.recv(BUFFER)
    except socket.error as e:
        print("Failed to receive data.")
        sys.exit()

    # Print the message to the screen
    print(f"Client message: {message_bytes.decode()}.")

    # Send an acknowledgement (e.g., integer of 1) to the client
    try:
        acknowledgement = socket.htons(1)
        acknowledgement_bytes = acknowledgement.to_bytes(4, 'little')
        connection.send(acknowledgement_bytes)
    except socket.error as e:
        print('Failed to send data.')
        sys.exit()

    tcp_server_socket.close()


def part2(port):
    print("********** PART 2 **********")
    host = 'student00.ischool.illinois.edu'
    sin = (host, int(port))

    # Loop that ensures that server stays up
    while True:
        # Datagram socket for TCP
        try:
            tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        except socket.error as e:
            print('Failed to create socket.')
            sys.exit()

        # Bind the socket to address
        try:
            opt = 1
            tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt)
            tcp_server_socket.bind(sin)
        except socket.error as e:
            print('Failed to bind socket.')
            sys.exit()

        # Start listening
        try:
            tcp_server_socket.listen()
            print("Waiting for connections on port 41014...")
        except socket.error as e:
            print("Failed to wait for connection.")
            sys.exit()

        # Accept the connection and record the address of the client socket
        try:
            connection, address = tcp_server_socket.accept()
            print(f"Connection established.")
        except socket.error as e:
            print("Failed to accept the connection.")
            sys.exit()

        # Loop for receiving messages
        while True:
            try:
                message_bytes = connection.recv(BUFFER)
                message = message_bytes.decode()
                message_split = message.split(' ')

            except socket.error as e:
                print('Failed to receive message.')
                sys.exit()

            # DN
            if message_split[0] == "DN":
                filename = message_split[1]
                if os.path.isfile(filename): 
                    file_size = os.path.getsize(filename)
                    file_size_bytes = file_size.to_bytes(4, 'little')
                    connection.send(file_size_bytes)
                else:
                    acknowledgement = socket.htonl(-1)
                    acknowledgement = acknowledgement.to_bytes(4, 'little')
                    connection.send(acknowledgement)

                if file_size_bytes != -1:
                    with open(filename, 'rb') as f:
                        data = f.read()
                        connection.sendall(data)
                        f.close()
                    print(f"{filename} was successfully transferred to the client.")

            # UP
            if message_split[0] == "UP":
                try:
                    message_bytes = connection.recv(BUFFER)
                    filesize = int.from_bytes(message_bytes, 'little')

                except socket.error as e:
                    print('Failed to receive data.')
                    sys.exit()
                if filesize == -1:
                    print('Error. File not found.')
                    continue
                else:
                    print(f'File size: {filesize}')
                    data = b''
                    while len(data) < filesize:
                        toRead = filesize - len(data)
                        if toRead > BUFFER:
                            packet = connection.recv(BUFFER)
                        else:
                            packet = connection.recv(filesize - len(data))
                        data += packet
                    with open(message_split[1], 'wb') as outFile:
                        outFile.write(data)
                    print('File transfer complete.')
                    continue

            # RM
            if message_split[0] == "RM":
                filename = message_split[1]
                if os.path.isfile(filename):
                    acknowledgement = socket.htonl(1)
                    acknowledgement = acknowledgement.to_bytes(4, 'little')
                    connection.send(acknowledgement)
                    confirmation = connection.recv(BUFFER)
                    confirmation = confirmation.decode()
                    if confirmation == 'Yes' or confirmation == 'yes' or confirmation == 'y':
                        os.remove(filename)
                        print(f"{filename} was successfully removed from the server.")
                else:
                    print(f"File {filename} does not exist on the server.")

            # LS
            if message_split[0] == "LS":
                files = os.listdir()
                files_string = ""
                if len(files) == 0:
                    files_string = "No files in directory."
                else:
                    for file in files:
                        files_string += file + " "
                    files_string = files_string[:-1]
                connection.send(files_string.encode())

            # MKDIR
            if message_split[0] == "MKDIR":
                directory_name = message_split[1]
                try:
                    if os.path.isdir(directory_name):
                        print(f"Directory {directory_name} already exists.")
                        acknowledgement = socket.htonl(-2)
                        acknowledgement = acknowledgement.to_bytes(4, 'little')
                        connection.send(acknowledgement)
                    else:
                        os.mkdir(directory_name)
                        acknowledgement = socket.htonl(1)
                        acknowledgement = acknowledgement.to_bytes(4, 'little')
                        connection.send(acknowledgement)
                        print(f"Directory {directory_name} was successfully created.")
                except OSError:
                    print(f"Creation of the directory {directory_name} failed.")
                    acknowledgement = socket.htonl(-1)
                    acknowledgement = acknowledgement.to_bytes(4, 'little')
                    connection.send(acknowledgement)


            # RMDIR
            if message_split[0] == "RMDIR":
                directory_name = message_split[1]
                try:
                    if os.path.isdir(directory_name):
                        if len(os.listdir(directory_name)) == 0:
                            acknowledgement = socket.htonl(1)
                            acknowledgement = acknowledgement.to_bytes(4, 'little')
                            connection.send(acknowledgement)
                            confirmation = connection.recv(BUFFER)
                            confirmation = confirmation.decode()
                            if confirmation == 'Yes' or confirmation == 'yes' or confirmation == 'y':
                                os.rmdir(directory_name)
                                print(f"Directory {directory_name} was successfully removed.")
                        else:
                            acknowledgement = socket.htonl(-2)
                            acknowledgement = acknowledgement.to_bytes(4, 'little')
                            connection.send(acknowledgement)
                            print(f"Directory {directory_name} is not empty.")
                except OSError:
                    print(f"Deletion of the directory {directory_name} failed.")
                    acknowledgement = socket.htonl(-1)
                    acknowledgement = acknowledgement.to_bytes(4, 'little')
                    connection.send(acknowledgement)

            # CD
            if message_split[0] == "CD":
                directory_name = message_split[1]
                try:
                    if os.path.isdir(directory_name):
                        acknowledgement = socket.htonl(1)
                        acknowledgement = acknowledgement.to_bytes(4, 'little')
                        connection.send(acknowledgement)
                        os.chdir(directory_name)
                        print(f"Current directory: {os.getcwd()}")
                    else:
                        acknowledgement = socket.htonl(-2)
                        acknowledgement = acknowledgement.to_bytes(4, 'little')
                        connection.send(acknowledgement)
                        print(f"Directory {directory_name} does not exist.")
                except OSError:
                    print(f"Changing directory to {directory_name} failed.")
                    acknowledgement = socket.htonl(-1)
                    acknowledgement = acknowledgement.to_bytes(4, 'little')
                    connection.send(acknowledgement)

            # QUIT
            if message_split[0] == 'QUIT':
                print('Connection closed.\n')
                tcp_server_socket.close()
                break


if __name__ == '__main__':
    if len(sys.argv) == 1:
        part1()
    else:
        part2(sys.argv[1])
