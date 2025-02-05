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
        self.is_my_turn = False

        # Bind the on_close method to the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_dark_mode(self):
        """
        Setup dark mode UI
        :return: None
        """
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
        """
        Setup main page
        :return: None
        """
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

        ttk.Label(self.main_frame, text=f"Your name: {self.name}", font=("Arial", 12, "bold")).grid(row=1, column=0, pady=5, sticky="n")

        # Buttons
        self.btn_new = ttk.Button(self.main_frame, text="New server", command=self.setup_new_server_page)
        self.btn_join = ttk.Button(self.main_frame, text="Join server", command=self.setup_join_server_page)
        self.btn_quit = ttk.Button(self.main_frame, text="Quit game", command=self.root.quit).grid

        self.btn_new.grid(row=2, column=0, pady=10, padx=10, sticky="ew")
        self.btn_join.grid(row=3, column=0, pady=10, padx=10, sticky="ew")
        self.btn_quit(row=4, column=0, pady=10, padx=10, sticky="ew")

        if self.client_socket is None:
            self.btn_new['state'] = "disabled"
            self.btn_join['state'] = "disabled"

        # Server Status Label
        server_status_label = ttk.Label(
            self.main_frame,
            text=self.main_message,
            font=("Arial", 10),
            foreground="green" if self.client_socket else "red",
        )
        server_status_label.grid(row=5, column=0, pady=20, sticky="s")

    def setup_new_server_page(self):
        """
        Setup new server page
        :return: None
        """
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
        server_name_entry.focus_set()
        server_name_entry.grid(row=1, column=0, pady=(30, 10), padx=10, sticky="n")

        # "Ok" Button
        def on_ok():
            server_name = server_name_entry.get()

            # Send request to create a new server
            self.client_socket.send((ClientAPI.NEW_SERVER + '/' + server_name).encode(FORMAT))

            # Get the response from the server
            msg = self.client_socket.recv(1024).decode(FORMAT)

            response = json.loads(msg)  # Assuming the server returns a JSON with server details and players

            if response['status'] == "success":
                self.current_server = response['name']
                self.setup_lobby_page(server_name, response['players'])
            else:
                print(response['msg'])

        # Bind Enter key to the on_ok function
        server_name_entry.bind("<Return>", lambda event: on_ok())

        ttk.Button(self.new_server_frame, text="Ok", command=on_ok).grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        # "Back" Button
        ttk.Button(self.new_server_frame, text="Back", command=self.setup_main_page).grid(row=3, column=0, pady=10,
                                                                                          padx=10, sticky="ew")

    def setup_join_server_page(self):
        """
        Setup join server page
        :return: None
        """
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
            selected_server_name = selected_server.split(' - ')[0]

            # Send request to join the server
            self.client_socket.send((ClientAPI.JOIN_SERVER + '/' + selected_server_name).encode(FORMAT))
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

    def setup_lobby_page(self, server_name: str, users: list[str]):
        """
        Setup lobby page
        :param server_name: Name of the server
        :param users: List of users
        :return: None
        """
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
            print(json.loads(response)['message'])
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


    def automatic_update_lobby(self, players_listbox: tk.Listbox, start_button: ttk.Button):
        """
        Send request to the server forever to get updates about the server
        :param players_listbox: Listbox of players
        :param start_button: Button for start
        :return: None
        """
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
                current_player = response['current_player']

                self.is_my_turn = current_player == self.name
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
        """
        Setup the game page
        :param server_name: Server name
        :param players: List of players name
        :param board_state: Matrix of the board
        :return:
        """
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
                font=("Arial", 12, "bold") if player == self.name else ("Arial", 12),
                anchor="w",
            ).pack(anchor="w", pady=5)

        # Quit Game Button
        def on_quit_game():
            self.client_socket.send(ClientAPI.EXIT_SERVER.encode(FORMAT))
            response = self.client_socket.recv(1024).decode(FORMAT)
            print(json.loads(response)['message'])
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
        """
        Send request to the server forever to get updates about the server
        :param btn_list: The list of buttons of the board
        :return: None
        """
        # Loop forever while the first button (at least) is existing
        while not self.is_my_turn and btn_list[0][0].winfo_exists():


            try:
                self.client_socket.send((ClientAPI.GET_SERVER + '/' + self.current_server).encode(FORMAT))
                msg = self.client_socket.recv(1024).decode(FORMAT)
            except OSError:
                break

            response = json.loads(msg)

            updated_board = response['board']
            current_player = response['current_player']
            winner_tuple = response['winner']

            print("Update board")
            end_game = self.update_board(current_player, btn_list, updated_board, winner_tuple)

            if end_game:
                break

            time.sleep(0.5)

    def update_board(self, current_player, btn_list, updated_board, winner_tuple):
        """
        Update the board game
        :param current_player: Symbol of the current player
        :param btn_list: List of buttons of the board
        :param updated_board: Matrix of the board
        :param winner_tuple: A tuple containing the winner along with his winning cells
        :return: None
        """
        # Determine if it's the player's turn
        self.is_my_turn = current_player == self.name

        # Update the game page with new board and players
        for i in range(len(btn_list)):
            for j in range(len(btn_list)):
                btn_list[i][j].config(text=updated_board[i][j])
                if self.is_my_turn:
                    btn_list[i][j]["state"] = "normal"
                else:
                    btn_list[i][j]["state"] = "disabled"

                if updated_board[i][j] != 0:
                    btn_list[i][j]["state"] = "disabled"

        # If there is a winner
        if winner_tuple[0] != 0:
            winner: tuple[str, list[tuple[int, int]]] = winner_tuple

            for (x, y) in winner[1]:

                if self.name == winner[0]:
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
                self.display_winner_overlay(winner[0])

            return True

        # If the board is full
        if all(cell != 0 for row in updated_board for cell in row):
            self.display_winner_overlay("")
            return True
        return False

    def display_winner_overlay(self, winner_name):
        """
        Display the winner on the window
        :param winner_name: Name of the winner
        :return: None
        """
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
        """
        Function called when the player is making a move
        :param x: x-position of the board
        :param y: y-position of the board
        :param btn_list: list of buttons of the board
        :return: None
        """
        # Send the move to the server
        move_message = f"{ClientAPI.MAKE_MOVE}/{self.current_server}/{x}/{y}"
        self.client_socket.send(move_message.encode(FORMAT))

        # Receive the updated board state and player turn
        response = self.client_socket.recv(1024).decode(FORMAT)
        response_data = json.loads(response)

        if response_data['status'] == "success":
            updated_board = response_data['board']
            current_player = response_data['current_player']
            winner_tuple = response_data['winner']

            # Update the game page with new board and players
            self.update_board(current_player, btn_list, updated_board, winner_tuple)

            # If it's no longer the player's turn, restart the thread
            if not self.is_my_turn:
                update_thread = threading.Thread(target=self.automatic_update_game, args=[btn_list], daemon=True)
                update_thread.start()

        else:
            print('failed to make move')  # Log error or invalid move

    def clear_frame(self):
        """
        Destroy all the children widgets
        :return: None
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_close(self):
        """
        Close socket before closing the application
        :return:
        """
        if self.client_socket is not None:
            self.client_socket.close()

        self.root.destroy()

def setup_socket():
    """
    Setup the client socket and connect to the server
    :return: client_socket, name, main_message
    """
    try:
        # Set up the client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set a timeout of 3 seconds for the requests
        client_socket.settimeout(3.0)

        client_socket.connect(ADDR)
        main_message = f"Connected to host {HOST} at port {PORT}"
        client_socket.send(ClientAPI.GET_MY_NAME.encode(FORMAT))
        name = client_socket.recv(1024).decode(FORMAT)

    except (ConnectionRefusedError, TimeoutError):
        # If the connection is refused, tell it to the client
        client_socket = None
        main_message = f"Error: cannot connect to host {HOST} at port {PORT}"
        name = None

    return client_socket, name, main_message

def main():

    # Setup client socket
    client_socket, name, main_message = setup_socket()

    root = tk.Tk()
    TicTacToeApp(root, client_socket, name, main_message)
    root.mainloop()

if __name__ == "__main__":
    main()

