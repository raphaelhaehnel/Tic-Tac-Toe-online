import socket
import threading

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000  # The port used by the server
FORMAT = 'utf-8'
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(ADDR)

print("Choose 'new server' or 'join server' or 'quit':")
msg = input()
client_socket.send(msg.encode(FORMAT))

if msg == "new server":

    while True:
        print("Enter the name of the server:")

        msg = input()

        if msg == "back":
            client_socket.send(msg.encode(FORMAT))
            break

        client_socket.send(msg.encode(FORMAT))

        # Get the response from the server
        msg = client_socket.recv(1024).decode(FORMAT)
        print(f"Response: {msg}")

        if msg == "Name already exists":
            print("Name already exists")
        else:
            print("Name available")
            break


elif msg == "join server":

    # Get the number of games
    n_games = client_socket.recv(1024).decode(FORMAT)
    print(f"{int(n_games)} servers available")

    for i in range(int(n_games)):
        msg = client_socket.recv(1024).decode(FORMAT)
        print(f"Server {i}: {msg}")

    print("Enter the name of the server you want to join:")

    msg = input()
    client_socket.send(msg.encode(FORMAT))


client_socket.close()
