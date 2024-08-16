import socket
import os
from utilities import SERVER_IP, SERVER_PORT, CHUNK_SIZE, client_send_file, client_receive_file


num_threads = 5

# request_list: list = [["", "big.pdf", "Download"]]
# request_list: list = [["", "big.pdf", "Download"]]
# request_list's format is [[file_path, file_name, "Upload"/"Download"], [file_path, file_name, "Upload"/"Download"], ...]

def process_request_list(client, request, address_saved_files, num_threads):
    action = request[1]
    if action == "Upload":
        client.send("u".encode())                
        client_send_file(client, request[0], num_threads)

    elif action == "Download":
        client.send("d".encode())
        client_receive_file(client, request[0], address_saved_files, num_threads)
    
    client.send("e".encode())
    client.close()
    return "Done"


def do_request(request, address_saved_files):
    if not os.path.isdir(address_saved_files):
        os.makedirs(address_saved_files)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if request[1] == "IP":
            client.connect((request[0], SERVER_PORT))
            server_msg = client.recv(CHUNK_SIZE).decode()
            if server_msg != "OK":
                return server_msg
            global SERVER_IP
            SERVER_IP = request[0]
            return "OK"
        else:
            client.connect((SERVER_IP, SERVER_PORT))

        server_msg = client.recv(CHUNK_SIZE).decode()
        if server_msg != "OK":
            return server_msg
        elif request[1] == "MAX_THREADS":
            global num_threads
            num_threads = int(request[0])
            client.send('t'.encode())
            client.send(num_threads.to_bytes(1, "big"))
            return str(num_threads)
        else:      
            return process_request_list(client, request, address_saved_files, num_threads)
    except Exception as e:
        return str(e)
    finally:
        client.close()

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
