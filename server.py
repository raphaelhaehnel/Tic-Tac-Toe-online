import socket
import threading

from game_server import GameServer, get_game_object
from player import Player
from client_api import ClientAPI
import json

# Define constants
HOST = '0.0.0.0'
PORT = 5000
FORMAT = 'utf-8'
ADDR = (HOST, PORT)

games_list = list()
games_list.append(GameServer("Game1"))

import random

# List of animal names
animal_names = [
    "Dragon", "Unicorn", "Pegasus", "Phoenix", "Griffin", "Centaur",
    "Mermaid", "Fairy", "Elf", "Dwarf", "Wyvern", "Wizard", "Werewolf",
    "Vampire", "Demon", "Angel", "Kraken"
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

        print(f"{player.name}: {msg[0]}")

        if msg[0] == ClientAPI.GET_MY_NAME:
            process_get_my_name(address, connection, player=player)

        elif msg[0] == ClientAPI.NEW_SERVER:
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
            process_exit_server(connection, player)
        else:
            # If the player is inside a game, exclude him from it
            if player.game is not None:
                current_server = get_game_object(games_list, player.game)
                current_server.remove_player(player)

                # If there is no player in the server
                if len(current_server.players) == 0:
                    # Remove the server from the list of servers
                    games_list.remove(current_server)
            break


def process_start(address, connection, msg):
    current_server = get_game_object(games_list, msg[1])
    if len(current_server.players) <= 1:
        response = {"status": "error", "message": "You need more people in your server"}
        response_json = json.dumps(response)
        connection.send(response_json.encode(FORMAT))
    else:
        current_server.start()
        print(f"{address} started server: {current_server.name}")

        response = {"status": "success", "message": f"You started the server {current_server.name}"}
        response_json = json.dumps(response)
        connection.send(response_json.encode(FORMAT))

def process_exit_server(connection: socket.socket, player: Player):
    current_server = get_game_object(games_list, player.game)
    current_server.remove_player(player)

    # If there is no player in the server
    if len(current_server.players) == 0:
        # Remove the server from the list of servers
        games_list.remove(current_server)

    response = {"status": "success", "message": f"You quit the server {current_server.name}"}
    response_json = json.dumps(response)
    connection.send(response_json.encode(FORMAT))

def process_join_server(address, connection, server_name, player):

    # Get the server corresponding to the index server 'msg'
    current_server = get_game_object(games_list, server_name)

    if current_server is None:
        response_data = {"status": "failed",
                         "message": "The game is not existing anymore"}

    elif current_server.has_started:
        response_data = {"status": "failed",
                         "message": "The game has already started"}
    else:

        # Add the player to the list of players of the server
        current_server.add_player(player)

        print(f"{address} joined server: {current_server.name}")
        response_data = {"status": "success",
                         "name": current_server.name,
                         "players": [player.name for player in current_server.players]}

    # Convert the list to JSON
    response = json.dumps(response_data)

    connection.send(response.encode(FORMAT))

def process_make_move(connection, player, server_name, x, y):

    # Get Game object
    current_server = get_game_object(games_list, server_name)

    # Try to make the move
    moved_done = current_server.make_move(player, x=int(x), y=int(y))

    # If the moved cannot be done
    if not moved_done:
        status = "failed"
    else:
        status = "success"

    response = {"status": status,
                "name": current_server.name,
                "board": current_server.board,
                "has_started": current_server.has_started,
                "current_player": current_server.current_player,
                "players": [player.name for player in current_server.players],
                "winner": current_server.winner}

    # Convert the list to JSON
    response_json = json.dumps(response)

    # Sends the list of servers as JSON
    connection.send(response_json.encode(FORMAT))

def process_get_server_list(connection):
    # Create a list of dictionaries with the names and players
    games_data = [{"name": game.name,
                   "players": [player.name for player in game.players],
                   "has_started": game.has_started} for game in games_list]

    # Convert the list to JSON
    servers_json = json.dumps(games_data)

    # Sends the list of servers as JSON
    connection.send(servers_json.encode(FORMAT))

def process_get_server(connection, server_name):

    # Get the server corresponding to the index server 'msg'
    current_server = get_game_object(games_list, server_name)

    # Create a list of dictionaries with the names and players
    response = {"status": "success",
                "name": current_server.name,
                "board": current_server.board,
                "has_started": current_server.has_started,
                "current_player": current_server.current_player,
                "players": [player.name for player in current_server.players],
                "winner": current_server.winner}

    # Convert the list to JSON
    server_json = json.dumps(response)

    # Sends the list of servers as JSON
    connection.send(server_json.encode(FORMAT))

def process_get_my_name(address, connection, player):

    connection.send(player.name.encode(FORMAT))
    print(f"{address} got name: {player.name}")


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
        servers_json = json.dumps(server_data)
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




