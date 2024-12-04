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

    def check_winner(self) -> tuple[int, list[tuple[int, int]]]:
        """
        Checks if there's a winner in the Tic-Tac-Toe game with the rule
        that the first player to get exactly 3 in a row wins.
        :return: A tuple containing the player number (1-based index) and a list of winning positions
                 if a winner exists, or (0, []) otherwise.
        """
        size = len(self.board)  # Size of the grid is (x+1)

        for player_symbol in range(1, len(self.players) + 1):  # Symbols start from 1 to x
            # Check rows
            for row_idx, row in enumerate(self.board):
                winner_positions = self.check_winner_helper(row, player_symbol, 3)
                if winner_positions:
                    return player_symbol, [(row_idx, col_idx) for col_idx in winner_positions]

            # Check columns
            for col_idx in range(size):
                column = [self.board[row_idx][col_idx] for row_idx in range(size)]
                winner_positions = self.check_winner_helper(column, player_symbol, 3)
                if winner_positions:
                    return player_symbol, [(row_idx, col_idx) for row_idx in winner_positions]

            # Check main diagonal
            main_diag = [self.board[i][i] for i in range(size)]
            winner_positions = self.check_winner_helper(main_diag, player_symbol, 3)
            if winner_positions:
                return player_symbol, [(i, i) for i in winner_positions]

            # Check anti-diagonal
            anti_diag = [self.board[i][size - 1 - i] for i in range(size)]
            winner_positions = self.check_winner_helper(anti_diag, player_symbol, 3)
            if winner_positions:
                return player_symbol, [(i, size - 1 - i) for i in winner_positions]

        # No winner yet
        return 0, []

    def check_winner_helper(self, line, symbol, count):
        """
        Checks if a given line (row, column, or diagonal) contains exactly 'count'
        consecutive occurrences of the given symbol.
        :param line: A list representing the row, column, or diagonal.
        :param symbol: The player's symbol to check for.
        :param count: The required number of consecutive symbols.
        :return: A list of indices where the streak occurs if found, otherwise an empty list.
        """
        streak = 0
        start_index = None

        for idx, cell in enumerate(line):
            if cell == symbol:
                if streak == 0:
                    start_index = idx
                streak += 1
                if streak == count:
                    return list(range(start_index, start_index + count))
            else:
                streak = 0
                start_index = None

        return []

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
