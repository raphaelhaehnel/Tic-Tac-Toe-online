# Online Tic-Tac-Toe

Final exercise for the course Computer network and Internet, Bar-Ilan University


## Usage
1. Run the server `server.py`.
2. Configure the file `config.json` and update the IP of the server (if the clients and the server are on the same computer, write localhost).
3. Run the client `client.py` (you can run multiple clients on multiple computer).


## Environment

- Operating System: Windows 10
- Python version: 3.10.5

## Files explanation

- `server.py`: Responsible for running the server and handle the clients.
- `client.py`: Implements the gui for the client.
- `api_client.py`: Define the API as an enumeration.
- `game.py`: Class representing a game
- `player.py`: Class representing a player

### Notes

1. When a user connects to the server, a random legendary creature name is assigned to him (he cannot choose his name).
2. If a server is left without any players, the server is automatically destroyed.

