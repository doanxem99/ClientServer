import socket
import os
import threading

SERVER_IP = "localhost"
SERVER_PORT = 12345

CLIENT_PORT = 34567
# Client will create a temporary server socket with this address to upload/download file to server using multithreading

CHUNK_SIZE = 1024  # Should be a small of 2 (1024 or 4096)
SHORT_NUM_LEN = 1  # Ex: segment index, length of file name
LONG_NUM_LEN = 4  # Ex: file size
# num_threads = 10


# segment_sizes: list = []

#--------------------------------------------------------------


def receive_all(sock, size):  # A counterpart of socket.sendall()
    fragments = []
    while size:
        chunk = sock.recv(size)
        if not chunk:
            break
        fragments.append(chunk)
        size -= len(chunk)
    return b"".join(fragments)


#--------------------------------------------------------------


def send_data(sock, data):  # Send small data unit (file name, file size, length of file name...) and file's byte chunk
    try:
        sock.sendall(data)
        msg = sock.recv(1).decode()
        while msg != "y":
            sock.sendall(data)
            msg = sock.recv(1).decode()
        return True
    except Exception as e:
        return False

def receive_data(sock, size):  # Receive small data unit (file name, file size, length of file name...) and file's byte chunk
    data = receive_all(sock, size)
    while len(data) < size:
        sock.send("n".encode())
        data = receive_all(sock, size)
    sock.send("y".encode())
    return data


#--------------------------------------------------------------


def send_file_segment(sock, file_path, file_size, idx, num_threads):
    with open(file_path, "rb") as file:
        segment_size = file_size//num_threads
        pos = segment_size*idx
        file.seek(pos)

        if idx == num_threads - 1:
            segment_size = file_size - segment_size*(num_threads - 1)

        data_len = CHUNK_SIZE
        while segment_size:
            if segment_size < CHUNK_SIZE:
                data_len = segment_size
            data = file.read(data_len)
            try:
                is_success = send_data(sock, data)
                if not is_success:
                    break
            except Exception as e:
                print("send_file_segment", str(e))
                break
            segment_size -= len(data)


def receive_file_segment(sock, tmp_file_path, file_size, idx, num_threads):
    segment_size = file_size//num_threads
    if idx == num_threads - 1:
        segment_size = file_size - segment_size*(num_threads - 1)
    
    with (open(os.path.join(tmp_file_path, f"{idx}.txt"), "wb")) as tmp_file:
        data_len = CHUNK_SIZE
        while segment_size:
            if segment_size < CHUNK_SIZE:
                data_len = segment_size
            data = receive_data(sock, data_len)
            tmp_file.write(data)
            segment_size -= len(data)


#--------------------------------------------------------------


def client_send_file(client, file_path, num_threads):
    file_name = os.path.basename(file_path)
    send_data(client, len(file_name).to_bytes(SHORT_NUM_LEN, "big"))
    send_data(client, file_name.encode())
    file_size = os.path.getsize(file_path)
    send_data(client, file_size.to_bytes(LONG_NUM_LEN, "big"))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tmp_sock:
        tmp_sock.bind((client.getsockname()[0], CLIENT_PORT))
        tmp_sock.listen(num_threads)
        client.send("y".encode())
        
        thread_socks = []
        for i in range(num_threads):
            conn, addr = tmp_sock.accept()
            thread_socks.append(conn)

        threads = []
        for i in range (num_threads):
            
            t = threading.Thread(target=send_file_segment, args=(thread_socks[i], file_path, file_size, i, num_threads,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
            
        for s in thread_socks:
            s.close()


def server_receive_file(conn, saved_path, num_threads):
    file_name_len = int.from_bytes(receive_data(conn, SHORT_NUM_LEN), "big")
    file_name = receive_data(conn, file_name_len).decode()
    file_size = int.from_bytes(receive_data(conn, LONG_NUM_LEN), "big")
    
    while True:
        if conn.recv(1).decode() == "y":
            break
    
    thread_socks = []
    for i in range(num_threads):
        tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmp_sock.connect((conn.getpeername()[0], CLIENT_PORT))
        thread_socks.append(tmp_sock)

    tmp_file_path = file_name + " segments"
    os.makedirs(tmp_file_path)

    threads = []
    for i in range (num_threads):
        t = threading.Thread(target=receive_file_segment, args=(thread_socks[i], tmp_file_path, file_size, i, num_threads,))
        t.start() 
        threads.append(t)
        
    for t in threads:
        t.join()

    for s in thread_socks:
        s.close()
        
    with open(os.path.join(os.getcwd(), saved_path, file_name), "wb") as file:
        for i in range(num_threads):
            with open(os.path.join(tmp_file_path, f"{i}.txt"), "rb") as tmp_file:
                while True:
                    data = tmp_file.read(CHUNK_SIZE)
                    if data:
                        file.write(data)
                    else:
                        break
            os.remove(os.path.join(tmp_file_path, f"{i}.txt"))
    os.rmdir(tmp_file_path)


#--------------------------------------------------------------


def server_send_file(conn, saved_path, num_threads):
    file_name_len = int.from_bytes(receive_data(conn, SHORT_NUM_LEN), "big")
    file_name = receive_data(conn, file_name_len).decode()
    file_path = os.path.join(saved_path, file_name)
    file_size = os.path.getsize(file_path)
    send_data(conn, file_size.to_bytes(LONG_NUM_LEN, "big"))

    while True:
        if conn.recv(1).decode() == "y":
            break
    
    thread_socks = []
    for i in range(num_threads):
        tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmp_sock.connect((conn.getpeername()[0], CLIENT_PORT))
        thread_socks.append(tmp_sock)

    threads = []
    for i in range (num_threads):
        t = threading.Thread(target=send_file_segment, args=(thread_socks[i], file_path, file_size, i, num_threads,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
        
    for s in thread_socks:
        s.close()


def client_receive_file(client, file_name, saved_path, num_threads):
    send_data(client, len(file_name).to_bytes(SHORT_NUM_LEN, "big"))
    send_data(client, file_name.encode())
    file_size = int.from_bytes(receive_data(client, LONG_NUM_LEN), "big")
    
    tmp_file_path = file_name + " segments"
    if not os.path.isdir(tmp_file_path):
        os.makedirs(tmp_file_path)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tmp_client:
        try:
            tmp_client.bind((client.getsockname()[0], CLIENT_PORT))
            tmp_client.listen(num_threads)
            client.send("y".encode())

            thread_socks = []
            for i in range(num_threads):
                conn, addr = tmp_client.accept()
                thread_socks.append(conn)

            threads = []
            for i in range (num_threads):
                t = threading.Thread(target=receive_file_segment, args=(thread_socks[i], tmp_file_path, file_size, i, num_threads,))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            for s in thread_socks:
                s.close()

            with open(os.path.join(saved_path, file_name), "wb") as file:
                for i in range(num_threads):
                    with open(os.path.join(tmp_file_path, f"{i}.txt"), "rb") as tmp_file:
                        while True:
                            data = tmp_file.read(CHUNK_SIZE)
                            if data:
                                file.write(data)
                            else:
                                break
                    os.remove(os.path.join(tmp_file_path, f"{i}.txt"))
            os.rmdir(tmp_file_path)
        except Exception as e:
            print(str(e))


def list_files(folder, level, conn):
    for file in os.listdir(folder):
        data = str(level) + ' ' + file
        conn.sendall(data.encode())
        if os.path.isdir(os.path.join(folder, file)):
            list_files(os.path.join(folder, file), level + 1, conn)


def server_send_name_files(conn, path):
    list_files(path, 1, conn)
    conn.sendall("e".encode())