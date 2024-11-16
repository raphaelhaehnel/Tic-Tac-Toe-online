import socket
import threading

# Define constants
HOST = '127.0.0.1'
PORT = 5000
FORMAT = 'utf-8'
ADDR = (HOST, PORT)


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

# connection.recv(1024).decode(FORMAT)

connection.send("Hello, I'm the server".encode(FORMAT))



