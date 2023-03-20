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

BUFFER = 4096


def part1():
    print("********** PART 1 **********")
    HOST = 'student01.ischool.illinois.edu'
    PORT = 41014

    # Message (in bytes) to test the code
    message = b"Hello World"

    # Convert the host name to the corresponding IP address
    # HOST = socket.gethostbyname(hostname)  # "127.0.0.1"
    sin = (HOST, PORT)

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


def part2(hostname, port):
    print("********** PART 2 **********")
    # Create the client address
    HOST = socket.gethostbyname(hostname)  # "127.0.0.1"
    sin = (HOST, int(port))

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

        if message_split[0] == 'DN':
            try:
                message_bytes = tcp_client_socket.recv(BUFFER)
                message_int = int.from_bytes(message_bytes, 'little')
                filesize = socket.ntohl(message_int)
            except socket.error as e:
                print('Failed to receive data.')
                sys.exit()
            if filesize == -1:
                print('Error. File not found.')
                continue
            else:
                print(f'File size: {filesize}')
                bytes_recieved = 0
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


                # while bytes_recieved < filesize:
                #     if filesize > BUFFER:
                #         print('Hello1')
                #         temp = tcp_client_socket.recv(BUFFER)
                #         print('Hello2')
                #         data += temp
                #         bytes_recieved += len(temp)
                #     elif filesize <= BUFFER:
                #         temp = tcp_client_socket.recv(filesize)
                #         data += temp
                #     else:
                #         print('ERROR')
                #     filesize -= len(temp)
                #     print(f'bytes: {bytes_recieved}')
                #     print(f'temp: {len(temp)}')
                #     print(f'filesize: {filesize}')
                # print('Hello')
                # with open(message_split[1], 'wb') as output_file:
                #     output_file.write(data)
                #     # output_file.close()
                print('File transfer complete.')
                continue

        if message_split[0] == 'UP':
            filename = message_split[1]
            try:
                message_bytes = tcp_client_socket.recv(BUFFER)
                message_int = int.from_bytes(message_bytes, 'little')
                acknowledgement = socket.ntohl(message_int)
            except socket.error as e:
                print('Failed to receive data.')
                sys.exit()
            if acknowledgement == -1:
                print('Server denied file transfer. File may already exist on server.')
                continue
            else:
                filesize = 0
                with open(message_split[1], 'rb') as f:
                    while True:
                        chunk = f.read(BUFFER)
                        if not chunk:
                            break
                        filesize += len(chunk)
                print(f'File size: {filesize}')
                message_bytes = bytes(str(filesize), 'utf-8')
                tcp_client_socket.send(message_bytes)
                with open(message_split[1], 'rb') as f:
                        data = f.read(BUFFER)
                        while data:
                            tcp_client_socket.send(data)
                            data = f.read(BUFFER)
                print('File transfer complete.')
                continue

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
                confirmation = input('Are you sure you want to delete this file?\n')
                if confirmation == 'Yes' or confirmation == 'yes' or confirmation == 'y' or confirmation == 'Y':
                    message_bytes = bytes('y', 'utf-8')
                    tcp_client_socket.send(message_bytes)
                else:
                    message_bytes = bytes('n', 'utf-8')
                    tcp_client_socket.send(message_bytes)
                    print('Delete abandoned by the user!')
                print('Directory removed.')
                continue
        
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
