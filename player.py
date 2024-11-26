class Player:

    def __init__(self, address: tuple[str, int], name: str):
        self.address: tuple[str, int] = address
        self.name: str = name
        self.game: str | None = None

    def join_server(self, game: str):
        self.game = game

    def quit_server(self):
        self.game = None

    def to_dict(self):
        return {
            "address": self.address,
            "name": self.name,
            "game": self.game
        }


