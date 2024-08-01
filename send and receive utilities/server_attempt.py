import socket
import os
from utilities import SERVER_IP, SERVER_PORT, server_send_file, server_receive_file


PATH = "Saved files"


if __name__ == "__main__":
    if not os.path.isdir(PATH):
        os.makedirs(PATH)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((SERVER_IP, SERVER_PORT))
        server.listen()
        conn, addr = server.accept()  # addr is a tuple containing client's IP and port
        while True:
            client_choice = conn.recv(1).decode()
            if client_choice == "a":
                print("[*] Received choice 'a'")
                server_receive_file(conn, PATH)

            elif client_choice == "b":
                print("[*] Received choice 'b'")
                server_send_file(conn, PATH)

            elif client_choice == "c":  # msg == "3"
                print("[*] Received choice 'c'")
                conn.close()
                break
            print()
