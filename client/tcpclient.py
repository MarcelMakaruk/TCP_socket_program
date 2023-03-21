# Import any necessary libraries below
import socket
import sys
import os

BUFFER = 4096


def part1():
    print("********** PART 1 **********")
    HOST = 'localhost'
    PORT = 41014
    sin = (HOST, PORT)

    # Message (in bytes) to test the code
    message = b"Hello World"

    # Create a datagram socket for TCP
    try:
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.error as e:
        print('Failed to create socket.')
        sys.exit()

    # Connect to the server
    try:
        tcp_client_socket.connect(sin)
    except socket.error as e:
        print("Failed to connect to the server.")

    # Send the message to the server
    try:
        tcp_client_socket.send(message)
    except socket.error as e:
        print("Failed to send data.")
        sys.exit()

    # Receive the acknowledgement from the server
    try:
        message_bytes = tcp_client_socket.recv(BUFFER)
        message_int = int.from_bytes(message_bytes, 'little')
        acknowledgement = socket.ntohs(message_int)
    except socket.error as e:
        print('Failed to receive data.')
        sys.exit()

    # Print the acknowledgement to the screen
    print(f'Acknowledgment: {acknowledgement}')

    # Close the socket
    tcp_client_socket.close()


def part2(host, port):
    print("********** PART 2 **********")
    sin = (host, int(port))

    # Create a datagram socket for TCP
    try:
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.error as e:
        print('Failed to create socket.')
        sys.exit()

    # Connect to the server
    try:
        print(f"Attempting to connect to the server: {sin}")
        tcp_client_socket.connect(sin)
        print("Connection established.")
    except socket.error as e:
        print("Failed to connect to the server.")

    while True:
        message = input('> ')
        message_split = message.split(' ')
        message_bytes = bytes(message, 'utf-8')
        try:
            tcp_client_socket.send(message_bytes)
        except socket.error as e:
            print('Failed to send message.')
            sys.exit()

        if message_split[0] == 'QUIT':
            print('Connection closed.')
            break

        # DN
        if message_split[0] == 'DN':
            try:
                message_bytes = tcp_client_socket.recv(BUFFER)
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
                        packet = tcp_client_socket.recv(BUFFER)
                    else:
                        packet = tcp_client_socket.recv(filesize - len(data))
                    data += packet
                with open(message_split[1], 'wb') as outFile:
                    outFile.write(data)
                print('File transfer complete.')
                continue

        # UP
        if message_split[0] == 'UP':
            filename = message_split[1]
            if os.path.isfile(filename):
                file_size = os.path.getsize(filename)
                file_size_bytes = file_size.to_bytes(4, 'little')
                tcp_client_socket.send(file_size_bytes)
            else:
                acknowledgement = socket.htonl(-1)
                acknowledgement = acknowledgement.to_bytes(4, 'little')
                tcp_client_socket.send(acknowledgement)

            if file_size_bytes != -1:
                with open(filename, 'rb') as f:
                    data = f.read()
                    tcp_client_socket.sendall(data)
                    f.close()
                print(f"{filename} was successfully transferred to the server.")

        # RM
        if message_split[0] == 'RM':
            try:
                message_bytes = tcp_client_socket.recv(BUFFER)
                message_int = int.from_bytes(message_bytes, 'little')
                acknowledgement = socket.ntohl(message_int)
            except socket.error as e:
                print('Failed to receive data.')
                sys.exit()
            if acknowledgement == -1:
                print('File not found.')
                continue
            else:
                confirmation = input('Are you sure you want to delete this file?\n')
                if confirmation == 'Yes' or confirmation == 'yes' or confirmation == 'y' or confirmation == 'Y':
                    message_bytes = bytes('y', 'utf-8')
                    tcp_client_socket.send(message_bytes)
                    print('File removed.')
                else:
                    message_bytes = bytes('n', 'utf-8')
                    tcp_client_socket.send(message_bytes)
                    print('Delete abandoned by the user!')
                continue

        # LS
        if message_split[0] == 'LS':
            try:
                message_bytes = tcp_client_socket.recv(BUFFER)
                message = message_bytes.decode('utf-8')
                for file in message.split(' '):
                    print(file)
            except socket.error as e:
                print('Failed to receive data.')
                sys.exit()
            continue

        # MKDIR
        if message_split[0] == 'MKDIR':
            try:
                message_bytes = tcp_client_socket.recv(BUFFER)
                message_int = int.from_bytes(message_bytes, 'little')
                acknowledgement = socket.ntohl(message_int)
            except socket.error as e:
                print('Failed to receive data.')
                sys.exit()
            if acknowledgement == -1:
                print('Error in making directory.')
                continue
            elif acknowledgement == -2:
                print('Directory already exists.')
                continue
            else:
                print('Directory created.')
                continue

        # RMDIR
        if message_split[0] == 'RMDIR':
            try:
                message_bytes = tcp_client_socket.recv(BUFFER)
                message_int = int.from_bytes(message_bytes, 'little')
                acknowledgement = socket.ntohl(message_int)
            except socket.error as e:
                print('Failed to receive data.')
                sys.exit()
            if acknowledgement == -1:
                print('Error in removing directory.')
                continue
            elif acknowledgement == -2:
                print('Directory does not exist.')
                continue
            else:
                confirmation = input('Are you sure you want to delete this directory?\n')
                if confirmation == 'Yes' or confirmation == 'yes' or confirmation == 'y' or confirmation == 'Y':
                    message_bytes = bytes('y', 'utf-8')
                    tcp_client_socket.send(message_bytes)
                    print('Directory removed')
                else:
                    message_bytes = bytes('n', 'utf-8')
                    tcp_client_socket.send(message_bytes)
                    print('Delete abandoned by the user!')
                continue

        # CD
        if message_split[0] == 'CD':
            try:
                message_bytes = tcp_client_socket.recv(BUFFER)
                message_int = int.from_bytes(message_bytes, 'little')
                acknowledgement = socket.ntohl(message_int)
            except socket.error as e:
                print('Failed to receive data.')
                sys.exit()
            if acknowledgement == -1:
                print('Error in changing directory.')
                continue
            elif acknowledgement == -2:
                print('The directory does not exist on server.')
                continue
            else:
                print('Changed current directory')
                continue


if __name__ == '__main__':
    if len(sys.argv) == 1:
        part1()
    else:
        part2(sys.argv[1], sys.argv[2])
