import socket
import os
import time
import utilities

IP = "localhost"
PORT = 12345


def print_menu():
    print("a. Upload file to server")
    print("b. Download file from server")
    print("c. Exit")


if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    while True:
        print()
        print_menu()
        choice = input("Your choice: ")
        if choice == "a":
            client.send("a".encode())
            utilities.client_send_file(client)

        elif choice == "b":
            client.send("b".encode())
            utilities.client_receive_file(client)

        elif choice == "c":
            client.send("c".encode())
            client.close()
            break

        else:
            print("Invalid choice!")
