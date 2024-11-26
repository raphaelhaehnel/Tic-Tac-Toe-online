class ClientAPI:

    # Create a new server with name "name". At the client, check name
    NEW_SERVER = "new_server" # + server_name

    # Get the list of the servers (multiple requests)
    GET_SERVERS_LIST = "get_server_list"

    # Get the infos of a server
    GET_SERVER = "get_server" # + server_name

    # Join the server named "named". No verification needed.
    JOIN_SERVER = "join_server" # + server_name

    # Make a move. Check if the player can play
    MAKE_MOVE = "make_move" # + server_name/x/y

    # Start a game
    START_GAME = "start" # + server_name

    # Exit the server during or before starting
    EXIT_SERVER = "exit_server"

    # Disconnect from the server
    QUIT = "quit"

    requests_list = [NEW_SERVER,
                     GET_SERVERS_LIST,
                     GET_SERVER,
                     JOIN_SERVER,
                     MAKE_MOVE,
                     EXIT_SERVER,
                     START_GAME,
                     QUIT]