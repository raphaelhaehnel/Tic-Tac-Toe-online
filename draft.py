import tkinter as tk
from http.client import responses
from tkinter import ttk
import socket
import threading
from api_client import ClientAPI
import json

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000  # The port used by the server
FORMAT = 'utf-8'
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT

class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.geometry("400x400")
        self.style = ttk.Style()

        try:
            # Set up the client socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(ADDR)
            self.main_message = f"Connected to host {HOST} at port {PORT}"
        except ConnectionRefusedError:

            # If the connection is refused, tell it to the client
            self.client_socket = None
            self.main_message = f"Error: cannot connect to host {HOST} at port {PORT}"

        # Apply dark mode styles
        self.setup_dark_mode()

        self.main_frame = None
        self.new_server_frame = None
        self.join_server_frame = None
        self.setup_main_page()

        ## Local parameters
        self.current_server = None # Name of the current server

        # Bind the on_close method to the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

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
            font=("Arial", 12),
            bd=0,
            selectbackground="#555555",
        )
        servers_listbox.grid(row=1, column=0, pady=(10, 20), padx=10, sticky="nsew")

        # Request server list from the server
        self.client_socket.send(ClientAPI.GET_SERVERS_LIST.encode(FORMAT))
        server_list_json = self.client_socket.recv(1024).decode(FORMAT)

        # Populate the listbox with server names
        server_list = json.loads(server_list_json)
        for server in server_list:
            servers_listbox.insert(tk.END, server['name'])

        # "Join" Button
        def on_join():
            selected_server = servers_listbox.get(servers_listbox.curselection())

            # Send request to join the server
            self.client_socket.send((ClientAPI.JOIN_SERVER + '/' + selected_server).encode(FORMAT))

            msg = self.client_socket.recv(1024).decode(FORMAT)
            response = json.loads(msg)

            print(f"{msg}")
            self.setup_lobby_page(response['name'], response['players'])

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

            self.client_socket.send((ClientAPI.EXIT_SERVER).encode(FORMAT))
            response = self.client_socket.recv(1024).decode(FORMAT)
            print(response)
            self.setup_main_page()

        ttk.Button(self.lobby_frame, text="Start", command=on_start).grid(
            row=2, column=0, pady=(10, 5), padx=10, sticky="ew"
        )

        # "Back to Main Menu" Button
        ttk.Button(self.lobby_frame, text="Back to Main Menu", command=on_exit).grid(
            row=3, column=0, pady=(5, 10), padx=10, sticky="ew"
        )

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