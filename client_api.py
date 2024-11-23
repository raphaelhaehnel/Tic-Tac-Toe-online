class ClientAPI:

    # Create a new server with name "name"
    # In the client, check if the name has no special characters
    NEW_SERVER = "new_server" # + server_name

    # Get the list of the servers (multiple requests)
    GET_SERVERS_LIST = "get_server_list"

    GET_SERVER = "get_server" # + server_name

    # Join the server named "named"
    # No verification is needed. The server must exist.
    JOIN_SERVER = "join_server" # + server_name

    # Exit the server during or before starting
    EXIT_SERVER = "exit_server"

    # Start a game
    START_GAME = "start" # + server_name

    # Disconnect from the server
    QUIT = "quit"

    requests_list = [NEW_SERVER,
                     GET_SERVERS_LIST,
                     JOIN_SERVER,
                     START_GAME,
                     QUIT]