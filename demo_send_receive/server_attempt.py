import socket
import os
import time
import utilities

IP = "localhost"
PORT = 12345
PATH = "Saved files"

if __name__ == "__main__":
    if not os.path.isdir(PATH):
        os.makedirs(PATH)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((IP, PORT))
        server.listen()
        conn, addr = server.accept()  # addr is a tuple containing client's IP and port
        while True:
            client_choice = conn.recv(1).decode()
            if client_choice == "a":
                print("Received choice 'a'")
                utilities.server_receive_file(conn, PATH)

            elif client_choice == "b":
                print("Received choice 'b'")
                utilities.server_send_file(conn, PATH)

            elif client_choice == "c":  # msg == "3"
                print("Received choice 'c'")
                conn.close()
                break
            print()
