class GameServer:

    def __init__(self, name: str):
        self.name: str = name
        self.players: list[tuple[str, int]] = []

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players.remove(player)
