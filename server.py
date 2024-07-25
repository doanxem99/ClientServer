import socket
import sys
import os
import time

# Create a TCP/IP socket and bind it to the server, then listen for incoming connections.
# When a client connects, the server will receive a message from the client and send the
# response of all the files and folders in the server's directory.

def files_folders(folder, level, connection):
    for file in os.listdir(folder):
        data = str(level) + ' ' + file
        connection.sendall(data.encode())
        if os.path.isdir(os.path.join(folder, file)):
            files_folders(os.path.join(folder, file), level + 1, connection)


def server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the server
    server_address = ('localhost', 54321)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)

    # Listen for incoming connections   
    sock.listen(1)
    cnt = 0
    while True:
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = sock.accept()
        
        try:
            print('connection from', client_address)

            # Receive the data in small chunks and retransmit it

            data = connection.recv(1024)
            if data:
                print('received "%s"' % data.decode())
                request = data.decode()
                if request == 'list':
                    connection.sendall((os.getcwd()).encode())
                    files_folders(os.getcwd() + "/dist", 1, connection)
            else:
                print('no more data from', client_address)
                break
        finally:
            # Clean up the connection
            connection.close()
    sock.close()


if __name__ == '__main__':
    server()
