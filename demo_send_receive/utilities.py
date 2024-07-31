import socket
import os
import time

CHUNK_SIZE = 4096  # Size of chunk when sending and receiving, 1024 is recommended
FILE_NAME_LEN = 256
NUMBER_LEN = 8  # Including file size, number of files at server

# Function with PRIVATE tag means that it should not be used outside of this (utilities.py) module

# FUNCTION FOR SENDING

def send_data(sock, data, size, padding):  # Used to send small data unit (file name, file size...) and file's byte chunk, PRIVATE
    if padding != b"":
        data = b"".join([data, padding * (size - len(data))])
    sock.sendall(data)
    while sock.recv(1).decode() != "y":
        sock.sendall(data)

def send_file(sock, file_path, file_size):  # PRIVATE
    with open(file_path, "rb") as file:
        read_len = CHUNK_SIZE
        while file_size:
            if file_size < CHUNK_SIZE:
                read_len = file_size
            data = file.read(read_len)
            send_data(sock, data, read_len, b"")
            file_size -= len(data)

def client_send_file(sock):
    file_path = input("File to send (enter the path with file name): ")
    while not os.path.exists(file_path) or os.path.isdir(file_path):
        file_path = input("Invalid path. Please enter the path again: ")

    file_name = os.path.basename(file_path)
    send_data(sock, file_name.encode(), FILE_NAME_LEN, b" ")
    file_size = os.path.getsize(file_path)
    send_data(sock, file_size.to_bytes(NUMBER_LEN, "big"), NUMBER_LEN, b"")

    start = time.time()
    send_file(sock, file_path, file_size)
    end = time.time()
    print("Done after", (end - start), "seconds")

def server_send_file(sock, path):
    server_files = os.listdir(path)
    send_data(sock, len(server_files).to_bytes(NUMBER_LEN, "big"), NUMBER_LEN, b"")  # send number of files at server to client
    if len(server_files) == 0:
        return
    else:
        for file in server_files:
            send_data(sock, file.encode(), FILE_NAME_LEN, b" ")  # send each file name to client

        file_name = receive_data(sock, FILE_NAME_LEN, b" ").decode()
        file_path = os.path.join(path, file_name)
        file_size = os.path.getsize(file_path)
        send_data(sock, file_size.to_bytes(NUMBER_LEN, "big"), NUMBER_LEN, b"")

        start = time.time()
        send_file(sock, file_path, file_size)
        end = time.time()
        print("Done after", (end - start), "seconds")


# FUNCTION FOR RECEIVING

def receive_all(sock, size):  # a counterpart of socket.sendall, PRIVATE
    fragments = []
    while size:
        chunk = sock.recv(size)
        if not chunk:
            return None
        fragments.append(chunk)
        size -= len(chunk)
    return b"".join(fragments)

def receive_data(sock, size, padding):  # Used to receive small data unit (file name, file size...) and file's byte chunk, PRIVATE
    data = receive_all(sock, size)
    while len(data) < size:
        sock.send("n".encode())
        data = receive_all(sock, size)
    sock.send("y".encode())
    if padding != b"":
        return data.strip(padding)
    else:
        return data

def receive_file(sock, file_path, file_size):  # PRIVATE
    with open(file_path, "wb") as file:
        write_len = CHUNK_SIZE
        while file_size:
            if file_size < CHUNK_SIZE:
                write_len = file_size
            data = receive_data(sock, write_len, b"")
            file.write(data)
            file_size -= len(data)

def client_receive_file(sock):
    number_of_files = int.from_bytes(receive_data(sock, NUMBER_LEN, b""), "big")
    print("\nList of file at server:")
    if number_of_files == 0:
        print("(No files)")
        return
    else:
        server_files = []
        for idx in range(number_of_files):
            temp_file_name = receive_data(sock, FILE_NAME_LEN, b" ").decode()
            print(f"{idx + 1}. {temp_file_name}")
            server_files.append(temp_file_name)

        file_idx = input("\nIndex of the file to download: ")
        while not file_idx.isdigit() or not 1 <= int(file_idx) <= number_of_files:
            file_idx = input("Invalid value! Please enter the index again: ")

        file_idx = int(file_idx) - 1
        file_name = server_files[file_idx]
        send_data(sock, file_name.encode(), FILE_NAME_LEN, b" ")
        file_size = int.from_bytes(receive_data(sock, NUMBER_LEN, b""), "big")

        print(f"File name is: {file_name}")
        print(f"File size is: {file_size} bytes")
        receive_file(sock, file_name, file_size)

def server_receive_file(sock, path):
    file_name = receive_data(sock, FILE_NAME_LEN, b" ").decode()
    file_size = int.from_bytes(receive_data(sock, NUMBER_LEN, b""), "big")

    print(f"File name is: {file_name}")
    print(f"File size is: {file_size} bytes")
    receive_file(sock, os.path.join(path, file_name), file_size)
