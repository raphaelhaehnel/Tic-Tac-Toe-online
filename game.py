from player import Player

class Game:
    """
    Define a single game.
    A game is created by the server, by request from a client
    """

    def __init__(self, name: str):
        """
        :param name: Name of the game
        """
        # Name of the game
        self.name: str = name

        # List of players that are currently inside the game
        self.players: list[Player] = list()

        # Flag if the game has started
        self.has_started: bool = False

        # A matrix defining the game board. It is defined by lists of int.
        self.board: list[list[int]] | None = None

        # Symbol of the player that must play now
        self.current_player: int = 1

        # A tuple containing the symbol of the winner and the winner cells coordinates
        self.winner: tuple[int, list[tuple[int, int]]] = 0, []

    def add_player(self, player: Player):
        """
        Add a player to the game
        :param player: A PLayer object
        :return: None
        """
        # Add the name of the server to the player game field
        player.join_game(self.name)

        # Add the player to the list of players
        self.players.append(player)

    def remove_player(self, player):
        """
        Remove a player from the game
        :param player: A PLayer object
        :return: None
        """
        player.quit_game()
        self.players.remove(player)

    def start(self):
        """
        Start the game
        :return: None
        """
        self.has_started = True
        self.generate_board()

    def generate_board(self):
        """
        Generate an empty board
        :return: None
        """
        x = len(self.players)
        self.board = [[0 for i in range(x+1)] for j in range(x+1)]

    def make_move(self, player: Player, x, y):
        """
        Make move for the player
        :param player: A PLayer object
        :param x: The x-position of the player move
        :param y: The y-position of the player move
        :return: True if the operation succeed, false otherwise
        """
        # If it's not your turn
        if self.players.index(player) + 1 != self.current_player:
            return False

        # If the cell is already taken
        if self.board[x][y] != 0:
            return False

        self.board[x][y] = self.current_player
        self.current_player = self.current_player % len(self.players) + 1
        self.winner = self.check_winner()
        return True

    def check_winner(self):
        size = len(self.board)
        win_length = 3

        # Function to check a line (row, column, or diagonal)
        def check_line(cells):
            if len(set(cells)) == 1 and cells[0] != 0:
                return cells[0]  # Winner is the player number (1, 2, etc.)
            return 0

        # Check rows
        for row in range(size):
            for col in range(size - win_length + 1):
                winner = check_line(self.board[row][col:col + win_length])
                if winner:
                    return winner, [(row, col + i) for i in range(win_length)]

        # Check columns
        for col in range(size):
            for row in range(size - win_length + 1):
                winner = check_line([self.board[row + i][col] for i in range(win_length)])
                if winner:
                    return winner, [(row + i, col) for i in range(win_length)]

        # Check diagonals (top-left to bottom-right)
        for row in range(size - win_length + 1):
            for col in range(size - win_length + 1):
                winner = check_line([self.board[row + i][col + i] for i in range(win_length)])
                if winner:
                    return winner, [(row + i, col + i) for i in range(win_length)]

        # Check diagonals (top-right to bottom-left)
        for row in range(size - win_length + 1):
            for col in range(win_length - 1, size):
                winner = check_line([self.board[row + i][col - i] for i in range(win_length)])
                if winner:
                    return winner, [(row + i, col - i) for i in range(win_length)]

        return 0, []  # No winner

def get_game_object(games: list[Game], name: str):
    """
    Given a list of games and a name of a specific game, get the corresponding game object from the list
    :param games: list of games
    :param name: name of a game
    :return: a Game object
    """
    for game in games:
        if game.name == name:
            return game
    return None
