import socket
import threading

from game_server import GameServer, get_game_object
from player import Player
from client_api import ClientAPI
import json

# Define constants
HOST = '127.0.0.1'
PORT = 5000
FORMAT = 'utf-8'
ADDR = (HOST, PORT)

games_list = list()
games_list.append(GameServer("Game1"))

import random

# List of animal names
animal_names = [
    "Lion", "Tiger", "Elephant", "Zebra", "Giraffe", "Kangaroo",
    "Panda", "Koala", "Wolf", "Fox", "Bear", "Cheetah", "Leopard",
    "Penguin", "Seal", "Dolphin", "Whale", "Shark", "Eagle", "Falcon"
]

# Set to track picked names
picked_names = set()


def get_random_animal():
    global picked_names
    if len(picked_names) >= len(animal_names):
        raise ValueError("All animal names have already been picked!")

    # Get a random name that hasn't been picked yet
    remaining_names = set(animal_names) - picked_names
    chosen_name = random.choice(list(remaining_names))
    picked_names.add(chosen_name)
    return chosen_name

def handle_client(connection: socket.socket, address: tuple[str, int]):
    """
    Handles a single client connection.
    :param connection:
    :param address:
    :return:
    """
    print(f"New connection at {address}")

    # Set up the new player
    player = Player(address, get_random_animal())

    while True:

        try:
            # Get a request from the client
            msg = connection.recv(1024).decode(FORMAT)
        except:
            break

        # Split the string according to the separator '/'
        msg = msg.split('/')

        if msg[0] == ClientAPI.NEW_SERVER:
            process_new_server(address, connection, server_name=msg[1], player=player)

        elif msg[0] == ClientAPI.GET_SERVERS_LIST:
            process_get_server_list(connection)

        elif msg[0] == ClientAPI.GET_SERVER:
            process_get_server(connection, server_name=msg[1])

        elif msg[0] == ClientAPI.JOIN_SERVER:
            process_join_server(address, connection, server_name=msg[1], player=player)

        elif msg[0] == ClientAPI.MAKE_MOVE:
            process_make_move(connection, player=player, server_name=msg[1], x=msg[2], y=msg[3])

        elif msg[0] == ClientAPI.START_GAME:
            process_start(address, connection, msg)

        elif msg[0] == ClientAPI.EXIT_SERVER:
            process_exit_server(address, connection, player)
        else:
            # If the player is inside a game, exclude him from it
            if player.game is not None:
                get_game_object(games_list, player.game).remove_player(player)
            break


def process_start(address, connection, msg):
    current_server = get_game_object(games_list, msg[1])
    if len(current_server.players) <= 1:
        response = {"status": "error", "message": "You need more people in your server"}
        response_json = json.dumps(response, indent=4)
        connection.send(response_json.encode(FORMAT))
    else:
        current_server.start()
        print(f"{address} started server: {current_server.name}")

        response = {"status": "success", "message": f"You started the server {current_server.name}"}
        response_json = json.dumps(response, indent=4)
        connection.send(response_json.encode(FORMAT))

def process_exit_server(address: tuple[str, int], connection: socket.socket, player: Player):
    current_server = get_game_object(games_list, player.game)
    current_server.remove_player(player)

    response = {"status": "success", "message": f"You quit the server {current_server.name}"}
    response_json = json.dumps(response, indent=4)
    connection.send(response_json.encode(FORMAT))

def process_join_server(address, connection, server_name, player):
    # Get the server corresponding to the index server 'msg'
    current_server = get_game_object(games_list, server_name)
    current_server.add_player(player)
    print(f"{address} joined server: {current_server.name}")
    server_data = {"name": current_server.name, "players": [player.name for player in current_server.players]}

    # Convert the list to JSON
    servers_json = json.dumps(server_data, indent=4)

    connection.send(servers_json.encode(FORMAT))

def process_make_move(connection, player, server_name, x, y):

    # Get Game object
    current_server = get_game_object(games_list, server_name)

    # Try to make the move
    moved_done = current_server.make_move(player, x=int(x), y=int(y))

    # Check if there is a winner
    winner = current_server.check_winner()

    # If the moved cannot be done
    if not moved_done:
        status = "failed"
    else:
        status = "success"

    response = {"status": status,
                "board": current_server.board,
                "players": [obj.to_dict() for obj in current_server.players],
                "winner": winner}
    response_json = json.dumps(response, indent=4)
    connection.send(response_json.encode(FORMAT))

def process_get_server_list(connection):
    # Create a list of dictionaries with the names and players
    games_data = [{"name": game.name, "players": [player.name for player in game.players]} for game in games_list]

    # Convert the list to JSON
    servers_json = json.dumps(games_data, indent=4)

    # Sends the list of servers as JSON
    connection.send(servers_json.encode(FORMAT))

def process_get_server(connection, server_name):

    # Get the server corresponding to the index server 'msg'
    current_server = get_game_object(games_list, server_name)

    # Create a list of dictionaries with the names and players
    game_data = {"name": current_server.name,
                 "players": [player.name for player in current_server.players],
                 "has_started": current_server.has_started,
                 "board": current_server.board}

    # Convert the list to JSON
    server_json = json.dumps(game_data, indent=4)

    # Sends the list of servers as JSON
    connection.send(server_json.encode(FORMAT))

def process_new_server(address, connection, server_name, player):
    # Check if the name of the new server is available
    if get_game_object(games_list, server_name) is not None:
        connection.send("Name already exists".encode(FORMAT))

    # Check if the name has special characters
    elif not server_name.isalnum():
        connection.send("Please use only alpha characters".encode(FORMAT))

    # If the name is correct
    else:
        print(f"{address} created server {server_name}")

        new_server = GameServer(server_name)
        new_server.add_player(player)
        games_list.append(new_server)

        server_data = {"name": new_server.name, "players": [player.name for player in new_server.players]}
        servers_json = json.dumps(server_data, indent=4)
        connection.send(servers_json.encode(FORMAT))

if __name__ == '__main__':

    # Initialize socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to address
    server_socket.bind(ADDR)

    # Listen to new clients
    server_socket.listen()

    while True:
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}\n")  # printing the amount of threads working

        print("Waiting for a client to connect...")
        connection, address = server_socket.accept()  # Waiting for client to connect to server (blocking call)

        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()




