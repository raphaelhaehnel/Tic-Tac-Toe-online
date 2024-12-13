import time
import tkinter as tk
from tkinter import ttk
import socket
import threading

from api_client import ClientAPI
import json

with open("config.json", "r") as file:
    json_file = json.load(file)

HOST = json_file['HOST']  # The server's hostname or IP address
PORT = json_file['PORT']  # The port used by the server
FORMAT = 'utf-8'
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT

class TicTacToeApp:
    def __init__(self, root: tk.Tk, client_socket: socket.socket, name: str, main_message: str):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.geometry("400x450")
        self.root.iconbitmap("tic-tac-toe.ico")
        self.style = ttk.Style()

        self.name: str | None = None
        self.client_socket: socket.socket | None = None
        self.main_message: str | None = None

        self.client_socket = client_socket
        self.name = name
        self.main_message = main_message

        # Apply dark mode styles
        self.setup_dark_mode()

        self.main_frame = None
        self.new_server_frame = None
        self.join_server_frame = None
        self.lobby_frame = None
        self.setup_main_page()

        ## Local parameters
        self.current_server = None # Name of the current server

        # Bind the on_close method to the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_game_page(self, server_name, players, board_state):
        self.clear_frame()

        # Outer frame for margins
        outer_frame = tk.Frame(self.root, bg="#2e2e2e")
        outer_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Configure root weights for responsiveness
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Inner frame for main content
        game_frame = tk.Frame(outer_frame, bg="#2e2e2e")
        game_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for responsiveness
        outer_frame.rowconfigure(0, weight=1)
        outer_frame.columnconfigure(0, weight=1)

        game_frame.rowconfigure(0, weight=1)  # Title row
        game_frame.rowconfigure(1, weight=4)  # Game board
        game_frame.rowconfigure(2, weight=1)  # Players list
        game_frame.rowconfigure(3, weight=1)  # Quit button row
        game_frame.columnconfigure(0, weight=1)

        # Title Label
        ttk.Label(
            game_frame,
            text=f"Game: {server_name}",
            font=("Arial", 16),
            anchor="center",
        ).grid(row=0, column=0, pady=10, sticky="n")

        # Game Board ((n+1)^2 Grid)
        board_frame = tk.Frame(game_frame, bg="#2e2e2e")
        board_frame.grid(row=1, column=0, pady=(10, 20), padx=10, sticky="nsew")

        n_players = len(players)
        btn_list: list[list[None|ttk.Button]] = [[None for _ in range(n_players+1)] for _ in range(n_players+1)]

        for i in range(n_players+1):
            board_frame.rowconfigure(i, weight=1)
            board_frame.columnconfigure(i, weight=1)
            for j in range(n_players+1):
                button_text = board_state[i][j] if board_state[i][j] != "" else " "
                btn = ttk.Button(
                    board_frame,
                    text=button_text,
                    command=lambda x=i, y=j: self.make_move(x, y, btn_list),
                    padding=5,
                )
                btn.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                btn_list[i][j] = btn # Add the button to the list of buttons

        # Players List with Symbols
        players_frame = tk.Frame(game_frame, bg="#2e2e2e")
        players_frame.grid(row=2, column=0, pady=(10, 20), padx=10, sticky="nsew")

        for player, symbol in zip(players, range(1, len(players)+1)):
            ttk.Label(
                players_frame,
                text=f"{player}: {symbol}",
                font=("Arial", 12),
                anchor="w",
            ).pack(anchor="w", pady=5)

        # Quit Game Button
        def on_quit_game():
            self.client_socket.send(ClientAPI.EXIT_SERVER.encode(FORMAT))
            response = self.client_socket.recv(1024).decode(FORMAT)
            print(response)
            self.setup_main_page()

        ttk.Button(
            game_frame,
            text="Quit Game",
            command=on_quit_game,
        ).grid(row=3, column=0, pady=(10, 20), padx=10, sticky="ew")

        # Start the automatic update thread once
        update_thread = threading.Thread(target=self.automatic_update_game, args=[btn_list], daemon=True)
        update_thread.start()


    def automatic_update_game(self, btn_list: list[list[tk.Button]]):

        # Loop forever while the first button (at least) is existing
        while btn_list[0][0].winfo_exists():

            try:
                self.client_socket.send((ClientAPI.GET_SERVER + '/' + self.current_server).encode(FORMAT))
                msg = self.client_socket.recv(1024).decode(FORMAT)
            except OSError:
                break

            response = json.loads(msg)

            updated_board = response['board']
            players = response['players']
            current_player = response['current_player']
            winner_tuple = response['winner']

            end_game = self.update_board(players, current_player, btn_list, updated_board, winner_tuple)

            if end_game:
                break

            time.sleep(0.5)

    def update_board(self, players, current_player, btn_list, updated_board, winner_tuple):

        # Update the game page with new board and players
        for i in range(len(players) + 1):
            for j in range(len(players) + 1):
                btn_list[i][j].config(text=updated_board[i][j])
                if players[current_player - 1] == self.name:
                    btn_list[i][j]["state"] = "normal"
                else:
                    btn_list[i][j]["state"] = "disabled"

                if updated_board[i][j] != 0:
                    btn_list[i][j]["state"] = "disabled"

        # If there is a winner
        if winner_tuple[0] != 0:
            winner: tuple[int, list[tuple[int, int]]] = winner_tuple

            for (x, y) in winner[1]:

                if self.name == players[winner[0] - 1]:
                    color_cells = 'green'
                else:
                    color_cells = 'red'

                # Color the winner cells
                style = ttk.Style()
                style.configure(style='W.TButton',
                                foreground=color_cells,
                                background=color_cells,
                                font=('Arial', 12, 'bold'))  # Set font to bold
                btn_list[x][y].config(style='W.TButton')

                # Display winning message overlay
                self.display_winner_overlay(players[winner[0] - 1])

            return True

        # If the board is full
        if all(cell != 0 for row in updated_board for cell in row):
            self.display_winner_overlay("")
            return True

        return False

    def display_winner_overlay(self, winner_name):
        # Determine the message and color based on the winner
        if winner_name == "":
            message = "It's a tie."
            color = "gray"
        elif winner_name == self.name:
            message = "You Won!"
            color = "green"
        else:
            message = f"You Lose.\nPlayer {winner_name} Won."
            color = "red"

        # Create a label to display the text
        overlay_label = tk.Label(
            self.root,
            text=message,
            fg=color,
            font=("Arial", 22, "bold"),
            justify="center"
        )
        overlay_label.place(relx=0.5, rely=0.5, anchor="center")

        # Prevent interaction with underlying widgets
        overlay_label.bind("<Button-1>", lambda e: None)

    def make_move(self, x, y, btn_list):
        # Send the move to the server
        move_message = f"{ClientAPI.MAKE_MOVE}/{self.current_server}/{x}/{y}"
        self.client_socket.send(move_message.encode(FORMAT))

        # Receive the updated board state and player turn
        response = self.client_socket.recv(1024).decode(FORMAT)
        response_data = json.loads(response)
        print(response)

        if response_data['status'] == "success":
            updated_board = response_data['board']
            players = response_data['players']
            current_player = response_data['current_player']
            winner_tuple = response_data['winner']

            # Update the game page with new board and players
            self.update_board(players, current_player, btn_list, updated_board, winner_tuple)

        else:
            print('failed to make move')  # Log error or invalid move

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_close(self):

        if self.client_socket is not None:
            self.client_socket.close()

        self.root.destroy()



def main():

    # Setup client socket
    client_socket, name, main_message = setup_socket()

    root = tk.Tk()
    TicTacToeApp(root, client_socket, name, main_message)
    root.mainloop()

if __name__ == "__main__":
    main()

