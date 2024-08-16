import socket
import threading
import os
from utilities import SERVER_PORT, server_send_file, server_receive_file, server_send_name_files

MAX_USER = 2
PATH = "Public Space"

def handle(client):
    addr = client.getpeername()
    num_threads = 5
    try: 
        while True:
            client_choice = client.recv(1).decode()
            if client_choice == "u":
                server_receive_file(client, PATH, num_threads)
            elif client_choice == "d":
                server_send_file(client, PATH, num_threads)
            elif client_choice == "l":
                server_send_name_files(client, PATH)
            elif client_choice == "e":
                client.close()
                break
            elif client_choice == "t":
                num_threads = int.from_bytes(client.recv(1))
                break
        print(f"[-] {addr} disconnected")
    except Exception as e:
        client.close()
        print(str(e))

def resolve_hang_on(server, threads):
    try:
        while True:
            conn, addr = server.accept()
            first_not_busy = -1
            print("hi2")
            for (i, thread) in enumerate(threads):
                if (thread == None) or (type(thread) is threading.Thread and not thread.is_alive()):
                    first_not_busy = i
                    break
            print("Success")
            
            if first_not_busy == -1:
                conn.sendall("WARNING: Server is currently full".encode())
                conn.close()
            else:
                conn.sendall("OK".encode())
                print(f"[+] {addr} connected")
                threads[first_not_busy] = threading.Thread(target=handle, args=(conn,))
                threads[first_not_busy].start()
    except Exception as e:
        print("reolve fn", str(e))
    print("exit")

if __name__ == "__main__":
    server_ip = socket.gethostbyname(socket.gethostname())
    if not os.path.isdir(PATH):
        os.makedirs(PATH)
    busy = True
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, SERVER_PORT))
    server.listen()
    
    threads = [None] * MAX_USER
    main_thread = threading.Thread(target=resolve_hang_on, args=(server, threads, ))
    first_time = True
    try:
        while True:
            if first_time:
                main_thread.start()
                first_time = False
            elif not main_thread.is_alive():
                main_thread.run()
                print(f"{server_ip}")

    except KeyboardInterrupt:
        print("Interrupt")
    except Exception as e:
        print("main", str(e))
    finally:
        #for thread in threads:
        #    if thread != None:
        #       thread.join()

        server.close()
