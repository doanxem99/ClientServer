import socket
import os
from utilities import SERVER_IP, SERVER_PORT, CHUNK_SIZE, client_send_file, client_receive_file




# request_list: list = [["", "big.pdf", "Download"]]
# request_list: list = [["", "big.pdf", "Download"]]
# request_list's format is [[file_path, file_name, "Upload"/"Download"], [file_path, file_name, "Upload"/"Download"], ...]

def process_request_list(client, request, address_saved_files):
    action = request[2]
    if action == "Upload":
        client.send("u".encode())                
        client_send_file(client, request[0])

    elif action == "Download":
        client.send("d".encode())
        client_receive_file(client, request[1], address_saved_files)
    
    client.send("e".encode())
    client.close()
    return "Done"


def do_request(request, address_saved_files):
    if not os.path.isdir(address_saved_files):
        os.makedirs(address_saved_files)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        server_msg = client.recv(CHUNK_SIZE).decode()
        if server_msg != "OK":
            return server_msg
        else:
            return process_request_list(client, request, address_saved_files)
    except Exception as e:
        return str(e)
    finally:
        client.close()

def server_settings(option, value):
    global SERVER_IP
    if option == "IP":
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((value, SERVER_PORT))
        except Exception as e:
            return str(e)
        SERVER_IP = value
    elif option == "MAX_THREADS":
        global MAX_THREADS
        MAX_THREADS = int(value)
        return str(MAX_THREADS)

def call_list():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data: list = []
    error: str = ""
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        server_msg = client.recv(CHUNK_SIZE).decode()
        if server_msg != "OK":
            print(server_msg)
        else:
            client.send('l'.encode())
            while True:
                item = client.recv(CHUNK_SIZE).decode()
                if item == "e":
                    break
                data.append(item)
            client.send('e'.encode())
        return (error, data)
            
    except Exception as e:
        error = str(e)
        return (error, data)
    finally:
        client.close()
