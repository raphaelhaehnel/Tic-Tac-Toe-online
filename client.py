import socket
import threading

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000  # The port used by the server
FORMAT = 'utf-8'
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(ADDR)

msg = client_socket.recv(1024).decode(FORMAT)

print(msg)

client_socket.close()
