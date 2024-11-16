import socket
import time

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000  # The port used by the server
FORMAT = 'utf-8'
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT


def start_client():
    client_socket.connect((HOST, PORT))  # Connecting to server's socket

    total_messages = input("Please enter # of messages you would like to send to server: ")
    client_socket.send(total_messages.encode(FORMAT))
    count = 0

    print(total_messages)
    for i in range(int(total_messages)):
        print(f"count: {i}, total: {total_messages}")
        new_message = input("Please enter message for server: ")

        client_socket.send(new_message.encode(FORMAT))  # Sending data to server
        print(f"[SENT DATA] {new_message}")  # Printing recieved data from server

        time.sleep(0.5)
        data = client_socket.recv(1024).decode(FORMAT)  # Receiving data from server
        print(f"[RECIEVED DATA] {data}\n")  # Printing recieved data from server
        count += 1

    client_socket.close()  # Closing client's connection with server (<=> closing socket)
    print("\n[CLOSING CONNECTION] client closed socket!")


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("[CLIENT] Started running")
    start_client()
    print("\nGoodbye client:)")