Programming Assignment 2
Marcel Makaruk, Jordan Carter, Michael Khalaf
-------------------------------------------------------------------------------------------

File List:

tcpclient.py
tcpserver.py

All .py files have been created using the most recent version of Python as of 3/20/23 and can been run sucessfully on machines "student00" and "student01."

To start the server and client, run the client and server files on separate machines.

After the server is started, the client will make a connection.

The client is able to pass the following commands, with extra arguments in brackets:

Download - "DN {target file}"
Downloads a file from the server to the client machine.

Upload - "UP {target file}"
Uploads a file from the client machine to the server.

Remove - "RM {target file}
Removes a file from the server.

List - "LS {target directory}"
Lists files in current directory.

Change Directory - "CD {target directory}"
Changes the active current directory to another.

Make Directory - "MKDIR {target directory}"
Creates a new directory.

Remove Directory - "RMDIR {target directory}"
Removes a directory from the server, if it is empty.

Quit - "QUIT" 
Closes the connection and exits the program.