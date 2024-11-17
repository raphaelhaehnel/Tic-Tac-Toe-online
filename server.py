import socket
import threading
from game_server import GameServer

# Define constants
HOST = '127.0.0.1'
PORT = 5000
FORMAT = 'utf-8'
ADDR = (HOST, PORT)

games_list = list()
games_list.append(GameServer("Game1"))


def check_if_name_exists(name: str, games_list: list[GameServer]):
    """
    For each GameList object in the list of games, checks if the given name is already taken.
    :param name:
    :param games_list:
    :return:
    """
    for game in games_list:
        if game.name == name:
            return True
    return False


# Initialize socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to address
server_socket.bind(ADDR)

# Listen to new clients
server_socket.listen()

print("Waiting for a client to connect...")

# Get the next client that is trying to connect
connection, address = server_socket.accept()

print(f"New connection at {address}")

# Get 'new server', 'join' or 'quit'
msg = connection.recv(1024).decode(FORMAT)
print(f"The user chose {msg}")

# If the client sent "new server"
if msg == "new server":

    while True:
        # Get the name of the server, or 'back'
        msg = connection.recv(1024).decode(FORMAT)
        print(f"Server name: {msg}")

        # If the client sent "back", do nothing
        if msg == "back":
            break
        else:

            # If the client sent the message name, check if the name already exists
            is_already_exist = check_if_name_exists(msg, games_list)

            if is_already_exist:
                connection.send("Name already exists".encode(FORMAT))
            else:
                connection.send("Name available".encode(FORMAT))
                games_list.append(GameServer(msg))
                break

# Else if the client sent "join server"
elif msg == "join server":

    # Send the number of games
    connection.send(str(len(games_list)).encode(FORMAT))

    for game in games_list:
        # Send the games names
        connection.send(game.name.encode(FORMAT))