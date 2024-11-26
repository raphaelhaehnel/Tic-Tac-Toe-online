from player import Player

class GameServer:

    def __init__(self, name: str):
        self.name: str = name
        self.players: list[Player] = list()
        self.has_started = False
        self.board: list[list[int]] | None = None
        self.current_player = 1

    def add_player(self, player: Player):
        player.join_server(self.name)
        self.players.append(player)

    def remove_player(self, player):
        player.quit_server()
        self.players.remove(player)

    def start(self):
        self.has_started = True
        self.generate_board()

    def generate_board(self):
        x = len(self.players)
        self.board = [[0 for i in range(x+1)] for j in range(x+1)]

    def make_move(self, player: Player, x, y):

        # It's not your turn
        if self.players.index(player) + 1 != self.current_player:
            return False

        # If the cell is already taken
        if self.board[x][y] != 0:
            return False

        self.board[x][y] = self.current_player
        self.current_player = self.current_player % len(self.players) + 1
        return True

    def check_winner(self):
        """
        Checks if there's a winner in the Tic-Tac-Toe game with the rule
        that the first player to get exactly 3 in a row wins.
        :return: The player number (1-based index) if a winner exists, or None otherwise.
        """
        size = len(self.board)  # Size of the grid is (x+1)

        for player_symbol in range(1, len(self.players) + 1):  # Symbols start from 1 to x
            # Check rows
            for row in self.board:
                if self.check_winner_helper(row, player_symbol, 3):
                    return self.players[player_symbol - 1]

            # Check columns
            for col in range(size):
                column = [self.board[row][col] for row in range(size)]
                if self.check_winner_helper(column, player_symbol, 3):
                    return self.players[player_symbol - 1]

            # Check main diagonal and anti-diagonal
            main_diag = [self.board[i][i] for i in range(size)]
            anti_diag = [self.board[i][size - 1 - i] for i in range(size)]

            if self.check_winner_helper(main_diag, player_symbol, 3) or self.check_winner_helper(anti_diag, player_symbol, 3):
                return self.players[player_symbol - 1]

        # No winner yet
        return None

    def check_winner_helper(self, line, symbol, count):
        """
        Checks if a given line (row, column, or diagonal) contains exactly 'count'
        consecutive occurrences of the given symbol.

        :param line: A list representing the row, column, or diagonal.
        :param symbol: The player's symbol to check for.
        :param count: The required number of consecutive symbols.
        :return: True if the line contains 'count' consecutive symbols, otherwise False.
        """
        streak = 0
        for cell in line:
            if cell == symbol:
                streak += 1
                if streak == count:
                    return True
            else:
                streak = 0
        return False


def get_game_object(games: list[GameServer], name: str):
    for game in games:
        if game.name == name:
            return game
    return None
