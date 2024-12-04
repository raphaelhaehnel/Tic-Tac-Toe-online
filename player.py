class Player:
    """
    Define a single player.
    A player is created by the server, when a new client is trying to connect to it
    """
    def __init__(self, address: tuple[str, int], name: str):
        """
        :param address: Tuple containing the address and the port of the player
        :param name: Name of the player
        """
        self.address: tuple[str, int] = address
        self.name: str = name
        self.game: str | None = None

    def join_game(self, game: str):
        """
        Add the name game to the game field
        :param game: Name of the game
        :return: None
        """
        self.game = game

    def quit_game(self):
        """
        Erase the game name from the game field
        :return: None
        """
        self.game = None

    def to_dict(self):
        """
        Convert the object to a dict
        :return: a dict describing the object.
        """
        return {
            "address": self.address,
            "name": self.name,
            "game": self.game
        }


