import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000  # The port used by the server
FORMAT = 'utf-8'
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT


def start_client():
    client_socket.connect((HOST, PORT))  # Connecting to server's socket

    message_from_server = client_socket.recv(1024).decode(FORMAT)
    print("[RECEIVED DATA] " + message_from_server)  # Printing recieved data from server
    name = input()
    client_socket.send(name.encode(FORMAT))
    print("[SENT DATA] " + name)  # Printing recieved data from server

    message_from_server = client_socket.recv(1024).decode(FORMAT)
    print("[RECEIVED DATA] " + message_from_server)  # Printing recieved data from server
    age = input()
    client_socket.send(age.encode(FORMAT))
    print("[SENT DATA] " + age)  # Printing recieved data from server

    message_from_server = client_socket.recv(1024).decode(FORMAT)
    print("[RECEIVED DATA] " + message_from_server)  # Printing recieved data from server
    profession = input()
    client_socket.send(profession.encode(FORMAT))
    print("[SENT DATA] " + profession)  # Printing recieved data from server

    final_message = client_socket.recv(1024).decode(FORMAT)  # Receiving data from server
    print("[RECEIVED DATA] " + final_message)  # Printing recieved data from server

    client_socket.close()  # Closing client's connection with server (<=> closing socket)
    print("\n[CLOSING CONNECTION] client closed socket!")


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("[CLIENT] Started running")
    start_client()
    print("\nGoodbye client:)")
