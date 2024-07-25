import socket
import sys

# Create a TCP/IP socket and connect to the server, then send a message to the server and 
# receive the response of all the files and folders in the server's directory.

def create_connection():
    try:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the server
        server_address = ('localhost', 54321)
        print('connecting to %s port %s' % server_address)
        sock.connect(server_address)
    except Exception as e:
        return str(e), None
    return "", sock

def call_list():
    address :str = ''
    data :list = []
    error :str = ''
    (error, sock) = create_connection()
    if error:
        return (error, address, data)
    try:
        # Send data
        message = 'list'
        print('sending "%s"' % message)
        sock.sendall(message.encode())

        # Look for the response
        item = sock.recv(1024)
        address = item.decode()
        while True:
            item = sock.recv(1024)
            data.append(item.decode())
            if not item:
                break
        return (error, address, data)
    
    except Exception as e:
        print(e)
        error = str(e)
        return (error, address, data)

    finally:
        print('closing socket')
        sock.close()


# if __name__ == '__main__':
#     client()