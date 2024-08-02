import socket
import os
import time
from concurrent.futures import ThreadPoolExecutor

SERVER_IP = "localhost"
SERVER_PORT = 12345

CLIENT_IP = "localhost"
CLIENT_PORT = 34567
# Client will create a temporary server socket with this address to upload/download file to server using multithreading

CHUNK_SIZE = 4096  # Should be a small of 2 (1024 or 4096)
SHORT_NUM_LEN = 1  # Ex: segment index, length of file name
LONG_NUM_LEN = 4  # Ex: file size at server
MAX_THREADS = 10


# FUNCTION FOR SENDING


def send_data(sock, data):  # Send small data unit (file name, file size, length of file name...) and file's byte chunk
    sock.sendall(data)
    while sock.recv(1).decode() != "y":
        sock.sendall(data)


def send_file_segment(sock, file_path, file_size, idx):
    with open(file_path, "rb") as file:
        segment_size = file_size//MAX_THREADS
        pos = segment_size*idx
        file.seek(pos)

        if idx == MAX_THREADS - 1:
            segment_size = file_size - segment_size*(MAX_THREADS - 1)

        data_len = CHUNK_SIZE
        while segment_size:
            if segment_size < CHUNK_SIZE:
                data_len = segment_size
            data = file.read(data_len)
            send_data(sock, data)
            segment_size -= len(data)


def client_send_file(sock):
    file_path = input("[?] File to send (enter the path with file name): ")
    while not os.path.exists(file_path) or os.path.isdir(file_path):
        file_path = input("[!] Invalid path (there may be some spaces at the start of file name that should be deleted)\n[?] Please enter the path again: ")

    file_name = os.path.basename(file_path)
    send_data(sock, len(file_name).to_bytes(SHORT_NUM_LEN, "big"))
    send_data(sock, file_name.encode())
    file_size = os.path.getsize(file_path)
    send_data(sock, file_size.to_bytes(LONG_NUM_LEN, "big"))

    start = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tmp_client:
        tmp_client.bind((CLIENT_IP, CLIENT_PORT))
        tmp_client.listen(MAX_THREADS)
        sock.send("y".encode())
        
        thread_socks = []
        for i in range(MAX_THREADS):
            conn, addr = tmp_client.accept()
            thread_socks.append(conn)

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            for i in range(MAX_THREADS):
                executor.submit(send_file_segment, thread_socks[i], file_path, file_size, i)
            
        for i in range(MAX_THREADS):
            thread_socks[i].close()
    end = time.time()
    print("[*] Done after", (end - start), "seconds")


def server_send_file(sock, path):
    server_files = os.listdir(path)
    send_data(sock, len(server_files).to_bytes(SHORT_NUM_LEN, "big"))  # send number of files at server to client
    if len(server_files) == 0:
        return
    else:
        for file_name in server_files:
            send_data(sock, len(file_name).to_bytes(SHORT_NUM_LEN, "big"))
            send_data(sock, file_name.encode())  # send each file name to client

        file_name_len = int.from_bytes(receive_data(sock, SHORT_NUM_LEN), "big")
        file_name = receive_data(sock, file_name_len).decode()
        file_path = os.path.join(path, file_name)
        file_size = os.path.getsize(file_path)
        send_data(sock, file_size.to_bytes(LONG_NUM_LEN, "big"))

        start = time.time()
        while True:
            if sock.recv(1).decode() == "y":
                break
        
        thread_socks = []
        for i in range(MAX_THREADS):
            tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tmp_sock.connect((CLIENT_IP, CLIENT_PORT))
            thread_socks.append(tmp_sock)

        
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            for i in range(MAX_THREADS):
                executor.submit(send_file_segment, thread_socks[i], file_path, file_size, i)
            
        for i in range(MAX_THREADS):
            thread_socks[i].close()
        end = time.time()
        print("[*] Done after", (end - start), "seconds")


# FUNCTION FOR RECEIVING


def receive_all(sock, size):  # A counterpart of socket.sendall()
    fragments = []
    while size:
        chunk = sock.recv(size)
        if not chunk:
            break
        fragments.append(chunk)
        size -= len(chunk)
    return b"".join(fragments)


def receive_data(sock, size):  # Receive small data unit (file name, file size, length of file name...) and file's byte chunk
    data = receive_all(sock, size)
    while len(data) < size:
        sock.send("n".encode())
        data = receive_all(sock, size)
    sock.send("y".encode())
    return data


def receive_file_segment(sock, tmp_file_path, file_size, idx):
    segment_size = file_size//MAX_THREADS
    if idx == MAX_THREADS - 1:
        segment_size = file_size - segment_size*(MAX_THREADS - 1)
    
    with (open(os.path.join(tmp_file_path, f"{idx}.txt"), "wb")) as tmp_file:
        data_len = CHUNK_SIZE
        while segment_size:
            if segment_size < CHUNK_SIZE:
                data_len = segment_size
            data = receive_data(sock, data_len)
            tmp_file.write(data)
            segment_size -= len(data)


def client_receive_file(sock):
    number_of_files = int.from_bytes(receive_data(sock, SHORT_NUM_LEN), "big")
    print("\n[*] List of file at server:")
    if number_of_files == 0:
        print("(No files)")
        return
    else:
        server_files = []
        for idx in range(number_of_files):
            file_name_len = int.from_bytes(receive_data(sock, SHORT_NUM_LEN), "big")
            file_name = receive_data(sock, file_name_len).decode()
            print(f"{idx + 1}. {file_name}")
            server_files.append(file_name)

        file_idx = input("\n[?] Index of the file to download: ")
        while not file_idx.isdigit() or not 1 <= int(file_idx) <= number_of_files:
            file_idx = input("[!] Invalid value!\n[?] Please enter the index again: ")

        file_idx = int(file_idx) - 1
        file_name = server_files[file_idx]
        send_data(sock, len(file_name).to_bytes(SHORT_NUM_LEN, "big"))
        send_data(sock, file_name.encode())
        file_size = int.from_bytes(receive_data(sock, LONG_NUM_LEN), "big")

        print(f"[*] File name is: {file_name}")
        print(f"[*] File size is: {file_size} bytes")
        
        start = time.time()
        tmp_file_path = file_name + " TMP"
        os.makedirs(tmp_file_path)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tmp_client:
            tmp_client.bind((CLIENT_IP, CLIENT_PORT))
            tmp_client.listen(MAX_THREADS)
            sock.send("y".encode())
            
            thread_socks = []
            for i in range(MAX_THREADS):
                conn, addr = tmp_client.accept()
                thread_socks.append(conn)

            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                for i in range(MAX_THREADS):
                    executor.submit(receive_file_segment, thread_socks[i], tmp_file_path, file_size, i)
                
            with open(file_name, "wb") as file:
                for i in range(MAX_THREADS):
                    with open(os.path.join(tmp_file_path, f"{i}.txt"), "rb") as tmp_file:
                        while True:
                            data = tmp_file.read(CHUNK_SIZE)
                            if data:
                                file.write(data)
                            else:
                                break
                    os.remove(os.path.join(tmp_file_path, f"{i}.txt"))
            os.rmdir(file_name + " TMP")
                
            for i in range(MAX_THREADS):
                thread_socks[i].close()            
        end = time.time()
        print("[*] Done after", (end - start), "seconds")


def server_receive_file(sock, path):
    file_name_len = int.from_bytes(receive_data(sock, SHORT_NUM_LEN), "big")
    file_name = receive_data(sock, file_name_len).decode()
    file_size = int.from_bytes(receive_data(sock, LONG_NUM_LEN), "big")

    print(f"[*] File name is: {file_name}")
    print(f"[*] File size is: {file_size} bytes")
    
    start = time.time()
    while True:
        if sock.recv(1).decode() == "y":
            break
    
    thread_socks = []
    for i in range(MAX_THREADS):
        tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmp_sock.connect((CLIENT_IP, CLIENT_PORT))
        thread_socks.append(tmp_sock)

    tmp_file_path = file_name + " TMP"
    os.makedirs(tmp_file_path)
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for i in range(MAX_THREADS):
            executor.submit(receive_file_segment, thread_socks[i], tmp_file_path, file_size, i)
        
    with open(os.path.join(path, file_name), "wb") as file:
        for i in range(MAX_THREADS):
            with open(os.path.join(tmp_file_path, f"{i}.txt"), "rb") as tmp_file:
                while True:
                    data = tmp_file.read(CHUNK_SIZE)
                    if data:
                        file.write(data)
                    else:
                        break
            os.remove(os.path.join(tmp_file_path, f"{i}.txt"))
    os.rmdir(file_name + " TMP")

    for i in range(MAX_THREADS):
        thread_socks[i].close()
    end = time.time()
    print("[*] Done after", (end - start), "seconds")
