import tkinter as tk
from tkinter import ttk

class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.geometry("400x400")
        self.style = ttk.Style()

        # Apply dark mode styles
        self.setup_dark_mode()

        self.main_frame = None
        self.new_server_frame = None
        self.join_server_frame = None
        self.setup_main_page()

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
        self.main_frame = tk.Frame(self.root, bg="#2e2e2e")
        self.main_frame.pack(pady=20, padx=20)

        ttk.Label(self.main_frame, text="Tic Tac Toe", font=("Arial", 20)).pack(pady=10)

        ttk.Button(self.main_frame, text="New server", command=self.setup_new_server_page).pack(pady=10)
        ttk.Button(self.main_frame, text="Join server", command=self.setup_join_server_page).pack(pady=10)
        ttk.Button(self.main_frame, text="Quit game", command=self.root.quit).pack(pady=10)

    def setup_new_server_page(self):
        self.clear_frame()
        self.new_server_frame = tk.Frame(self.root, bg="#2e2e2e")
        self.new_server_frame.pack(pady=20, padx=20)

        ttk.Label(self.new_server_frame, text="Create New Server", font=("Arial", 16)).pack(pady=10)
        ttk.Label(self.new_server_frame, text="Enter server name:").pack(pady=5)
        server_name_entry = ttk.Entry(self.new_server_frame, width=30)
        server_name_entry.pack(pady=10)

        def on_ok():
            server_name = server_name_entry.get()
            print(f"Server created: {server_name}")
            self.setup_main_page()

        ttk.Button(self.new_server_frame, text="Ok", command=on_ok).pack(pady=10)
        ttk.Button(self.new_server_frame, text="Back", command=self.setup_main_page).pack(pady=10)

    def setup_join_server_page(self):
        self.clear_frame()
        self.join_server_frame = tk.Frame(self.root, bg="#2e2e2e")
        self.join_server_frame.pack(pady=20, padx=20)

        ttk.Label(self.join_server_frame, text="Available Servers", font=("Arial", 16)).pack(pady=10)

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
        servers_listbox.pack(pady=10)

        # Mock data for available servers
        servers = ["Server 1", "Server 2", "Server 3"]
        for server in servers:
            servers_listbox.insert(tk.END, server)

        ttk.Button(self.join_server_frame, text="Back", command=self.setup_main_page).pack(pady=10)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()
