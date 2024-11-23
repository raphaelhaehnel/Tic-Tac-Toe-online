from player import Player

class GameServer:

    def __init__(self, name: str):
        self.name: str = name
        self.players: list[Player] = list()
        self.has_started = False

    def add_player(self, player: Player):
        player.join_server(self.name)
        self.players.append(player)

    def remove_player(self, player):
        player.quit_server()
        self.players.remove(player)

    def start(self):
        self.has_started = True

def get_game_object(games: list[GameServer], name: str):
    for game in games:
        if game.name == name:
            return game
    return None