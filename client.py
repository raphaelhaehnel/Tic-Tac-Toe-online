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
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.geometry("400x400")
        self.root.iconbitmap("tic-tac-toe.ico")
        self.style = ttk.Style()

        self.threads: list[threading.Thread] = [] # Initializes the threads

        self.name: str | None = None
        self.client_socket: socket.socket | None = None
        self.main_message: str | None = None

        # Setup the client socket
        self.setup_socket()

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

    def setup_socket(self):
        try:
            # Set up the client socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Set a timeout of 3 seconds for the requests
            self.client_socket.settimeout(3.0)

            self.client_socket.connect(ADDR)
            self.main_message = f"Connected to host {HOST} at port {PORT}"
            self.client_socket.send(ClientAPI.GET_MY_NAME.encode(FORMAT))
            self.name = self.client_socket.recv(1024).decode(FORMAT)

        except (ConnectionRefusedError, TimeoutError) as e:
            # If the connection is refused, tell it to the client
            self.client_socket = None
            self.main_message = f"Error: cannot connect to host {HOST} at port {PORT}"

    def setup_dark_mode(self):
        self.root.configure(bg="#2e2e2e")
        self.style.configure(
            "TLabel",
            background="#2e2e2e",
            foreground="#ffffff",
            font=("Arial", 12),
        )
        self.style.configure(
            "TButton",
            background="#ffffff",
            foreground="#000000",
            font=("Arial", 12),
            padding=5,
        )
        self.style.map(
            "TButton",
            background=[("active", "#dddddd")],  # Lighter gray on hover
            foreground=[("active", "#000000")],
        )

    def setup_main_page(self):
        self.clear_frame()

        # Outer frame for margins
        outer_frame = tk.Frame(self.root, bg="#2e2e2e")
        outer_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Margin around the content

        # Configure root weights for responsiveness
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Inner frame for main content
        self.main_frame = tk.Frame(outer_frame, bg="#2e2e2e")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for responsiveness
        outer_frame.rowconfigure(0, weight=1)
        outer_frame.columnconfigure(0, weight=1)

        self.main_frame.rowconfigure(0, weight=1)  # Title row
        self.main_frame.rowconfigure(1, weight=1)  # Buttons
        self.main_frame.rowconfigure(2, weight=1)  # Buttons
        self.main_frame.rowconfigure(3, weight=1)  # Buttons
        self.main_frame.rowconfigure(4, weight=1)  # Server status row
        self.main_frame.columnconfigure(0, weight=1)

        # Title Label
        ttk.Label(self.main_frame, text="Tic Tac Toe", font=("Arial", 20)).grid(row=0, column=0, pady=10, sticky="n")

        # Buttons
        ttk.Button(self.main_frame, text="New server", command=self.setup_new_server_page).grid(row=1, column=0,
                                                                                                pady=10, padx=10,
                                                                                                sticky="ew")
        ttk.Button(self.main_frame, text="Join server", command=self.setup_join_server_page).grid(row=2, column=0,
                                                                                                  pady=10, padx=10,
                                                                                                  sticky="ew")
        ttk.Button(self.main_frame, text="Quit game", command=self.root.quit).grid(row=3, column=0, pady=10, padx=10,
                                                                                   sticky="ew")

        # Server Status Label
        server_status_label = ttk.Label(
            self.main_frame,
            text=self.main_message,
            font=("Arial", 10),
            foreground="green" if self.client_socket else "red",
        )
        server_status_label.grid(row=4, column=0, pady=20, sticky="s")

    def setup_new_server_page(self):
        self.clear_frame()

        # Outer frame for margins
        outer_frame = tk.Frame(self.root, bg="#2e2e2e")
        outer_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Margin around the content

        # Configure root weights for responsiveness
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Inner frame for main content
        self.new_server_frame = tk.Frame(outer_frame, bg="#2e2e2e")
        self.new_server_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for responsiveness
        outer_frame.rowconfigure(0, weight=1)
        outer_frame.columnconfigure(0, weight=1)

        self.new_server_frame.rowconfigure(0, weight=1)  # Title row
        self.new_server_frame.rowconfigure(1, weight=1)  # Input field row
        self.new_server_frame.rowconfigure(2, weight=1)  # Ok button row
        self.new_server_frame.rowconfigure(3, weight=1)  # Back button row
        self.new_server_frame.columnconfigure(0, weight=1)

        # Title Label
        ttk.Label(
            self.new_server_frame,
            text="Create New Server",
            font=("Arial", 16),
            anchor="center",
        ).grid(row=0, column=0, pady=10, sticky="n")

        # Input Field
        ttk.Label(self.new_server_frame, text="Enter server name:").grid(row=1, column=0, pady=5, sticky="n")
        server_name_entry = ttk.Entry(self.new_server_frame, width=30)
        server_name_entry.grid(row=1, column=0, pady=(30, 10), padx=10, sticky="n")

        # "Ok" Button
        def on_ok():
            server_name = server_name_entry.get()

            # Send request to create a new server
            self.client_socket.send((ClientAPI.NEW_SERVER + '/' + server_name).encode(FORMAT))

            # Get the response from the server
            msg = self.client_socket.recv(1024).decode(FORMAT)

            response = json.loads(msg)  # Assuming the server returns a JSON with server details and players

            print(f"{msg}")
            # TODO: If the server is available, go to lobby
            self.current_server = response['name']
            self.setup_lobby_page(server_name, response['players'])

        ttk.Button(self.new_server_frame, text="Ok", command=on_ok).grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        # "Back" Button
        ttk.Button(self.new_server_frame, text="Back", command=self.setup_main_page).grid(row=3, column=0, pady=10,
                                                                                          padx=10, sticky="ew")

    def setup_join_server_page(self):
        self.clear_frame()

        # Outer frame for margins
        outer_frame = tk.Frame(self.root, bg="#2e2e2e")
        outer_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Add margins

        # Configure root weights for responsiveness
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Inner frame for main content
        self.join_server_frame = tk.Frame(outer_frame, bg="#2e2e2e")
        self.join_server_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for responsiveness
        outer_frame.rowconfigure(0, weight=1)
        outer_frame.columnconfigure(0, weight=1)

        self.join_server_frame.rowconfigure(0, weight=1)  # Title row
        self.join_server_frame.rowconfigure(1, weight=2)  # Listbox row
        self.join_server_frame.rowconfigure(2, weight=1)  # Buttons row
        self.join_server_frame.columnconfigure(0, weight=1)

        # Title Label
        ttk.Label(
            self.join_server_frame,
            text="Available Servers",
            font=("Arial", 16),
            anchor="center",
        ).grid(row=0, column=0, pady=10, sticky="n")

        # Servers Listbox
        servers_listbox = tk.Listbox(
            self.join_server_frame,
            width=40,
            height=10,
            bg="#444444",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            bd=0,
            # For selected items
            selectbackground="#555555",
        )
        servers_listbox.grid(row=1, column=0, pady=(10, 20), padx=10, sticky="nsew")

        # Request server list from the server
        self.client_socket.send(ClientAPI.GET_SERVERS_LIST.encode(FORMAT))
        server_list_json = self.client_socket.recv(1024).decode(FORMAT)

        # Populate the listbox with server names
        server_list = json.loads(server_list_json)
        print(server_list)
        for server in server_list:
            server_name = server['name']
            player_count = len(server['players'])  # Assuming this field contains the number of players
            has_started = server['has_started']  # Assuming this field indicates if the server has started

            # Format the display string
            display_text = f"{server_name} - Players: {player_count} - {'Started' if has_started else 'Waiting'}"

            # Add to listbox
            servers_listbox.insert(tk.END, display_text)

            # Color coding based on server status
            if has_started:
                servers_listbox.itemconfig(tk.END, {'fg': '#F06161'})  # Red for started servers
            else:
                servers_listbox.itemconfig(tk.END, {'fg': '#6AF066'})  # Green for waiting servers

        # "Join" Button
        def on_join():

            if not servers_listbox.curselection():
                return

            # Get the selected server from the listbox
            selected_server: str = servers_listbox.get(servers_listbox.curselection())

            # Extract the name from the string
            server_name = selected_server.split(' - ')[0]

            # Send request to join the server
            self.client_socket.send((ClientAPI.JOIN_SERVER + '/' + server_name).encode(FORMAT))
            msg = self.client_socket.recv(1024).decode(FORMAT)
            response = json.loads(msg)

            if response["status"] == "success":
                self.current_server = response['name']
                self.setup_lobby_page(response['name'], response['players'])
            else:
                print(f"{msg}")

        ttk.Button(self.join_server_frame, text="Join", command=on_join).grid(
            row=2, column=0, pady=(10, 5), padx=10, sticky="ew"
        )

        # "Back" Button
        ttk.Button(self.join_server_frame, text="Back", command=self.setup_main_page).grid(
            row=3, column=0, pady=(5, 10), padx=10, sticky="ew"
        )

    def setup_lobby_page(self, server_name, users):
        self.clear_frame()

        # Outer frame for margins
        outer_frame = tk.Frame(self.root, bg="#2e2e2e")
        outer_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Add margins

        # Configure root weights for responsiveness
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Inner frame for main content
        self.lobby_frame = tk.Frame(outer_frame, bg="#2e2e2e")
        self.lobby_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for responsiveness
        outer_frame.rowconfigure(0, weight=1)
        outer_frame.columnconfigure(0, weight=1)

        self.lobby_frame.rowconfigure(0, weight=1)  # Title row
        self.lobby_frame.rowconfigure(1, weight=2)  # Players list row
        self.lobby_frame.rowconfigure(2, weight=1)  # Buttons row
        self.lobby_frame.columnconfigure(0, weight=1)

        # Title Label
        ttk.Label(
            self.lobby_frame,
            text=f"Lobby: {server_name}",
            font=("Arial", 16),
            anchor="center",
        ).grid(row=0, column=0, pady=10, sticky="n")

        # Players Listbox
        players_listbox = tk.Listbox(
            self.lobby_frame,
            width=40,
            height=10,
            bg="#444444",
            fg="#ffffff",
            font=("Arial", 12),
            bd=0,
            selectbackground="#555555",
        )
        players_listbox.grid(row=1, column=0, pady=(10, 20), padx=10, sticky="nsew")

        # Populate players listbox
        for user in users:
            players_listbox.insert(tk.END, user)

        players_listbox.bind("<<ListboxSelect>>", None)

        # "Start" Button
        def on_start():
            # Notify the server to start the game
            self.client_socket.send((ClientAPI.START_GAME + '/' + server_name).encode(FORMAT))

            response = self.client_socket.recv(1024).decode(FORMAT)
            response_json = json.loads(response)

            print(response_json['message'])

            if response_json['status'] == 'error':
                pass  # Handle error
            else:
                print("Game started!")  # Replace with game logic or transition

        def on_exit():

            self.client_socket.send(ClientAPI.EXIT_SERVER.encode(FORMAT))
            response = self.client_socket.recv(1024).decode(FORMAT)
            print(response)
            self.current_server = None
            self.setup_main_page()

        start_button = ttk.Button(self.lobby_frame, text="Start", command=on_start)
        start_button.grid(row=2, column=0, pady=(10, 5), padx=10, sticky="ew")

        # Only the first to join the game can start it
        if users[0] != self.name:
            start_button['state'] = "disabled"

        # "Back to Main Menu" Button
        ttk.Button(self.lobby_frame, text="Back to Main Menu", command=on_exit).grid(
            row=3, column=0, pady=(5, 10), padx=10, sticky="ew"
        )

        thread = threading.Thread(target=self.automatic_update_lobby, args=[players_listbox, start_button], daemon=True)
        thread.start()

        self.threads.append(thread)
        #TODO delete the thread from the list when it finishes


    def automatic_update_lobby(self, players_listbox: tk.Listbox, start_button: ttk.Button):

        while players_listbox.winfo_exists():

            try:
                self.client_socket.send((ClientAPI.GET_SERVER + '/' + self.current_server).encode(FORMAT))
                msg = self.client_socket.recv(1024).decode(FORMAT)
            except OSError:
                break

            response = json.loads(msg)

            if response['has_started']:
                server_name = response['name']
                players = response['players']
                board_state = response['board']
                self.setup_game_page(server_name, players, board_state)
                break
            users = response['players']

            # If the first player left the game, checks if the current player is now
            # the first player
            if users[0] == self.name and start_button['state'] == 'disabled':
                start_button['state'] = "enabled"

            players_listbox.delete(0, tk.END)  # Deletes all items from index 0 to the end
            for user in users:
                players_listbox.insert(tk.END, user)

            print("Updated users list !")
            time.sleep(0.5)

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
        if not hasattr(self, "update_thread"):
            self.update_thread = threading.Thread(target=self.automatic_update_game, args=[btn_list], daemon=True)
            self.update_thread.start()

            self.threads.append(self.update_thread)
            # TODO delete the thread from the list when it finishes


    def automatic_update_game(self, btn_list: list[list[tk.Button]]):

        # Loop forever while the first button (at least) is existing
        while btn_list[0][0].winfo_exists():

            try:
                self.client_socket.send((ClientAPI.GET_SERVER + '/' + self.current_server).encode(FORMAT))
                msg = self.client_socket.recv(1024).decode(FORMAT)
            except OSError:
                break

            response = json.loads(msg)
            print(response)
            updated_board = response['board']
            players = response['players']
            current_player = response['current_player']
            winner_tuple = response['winner']

            is_winner = self.update_board(players, current_player, btn_list, updated_board, winner_tuple)

            if is_winner:
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
                                background=color_cells)
                btn_list[x][y].config(style='W.TButton')
            return True
        return False

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

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()