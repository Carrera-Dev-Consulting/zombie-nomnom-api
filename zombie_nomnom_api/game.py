import uuid
from zombie_nomnom import ZombieDieGame


class Game:
    game: ZombieDieGame
    id: str

    def __init__(self, *, game: ZombieDieGame, id: str = None) -> None:
        self.game = game
        self.id = id or str(uuid.uuid4())

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Game) and self.id == value.id


class GameMaker:
    def __init__(self) -> None:
        self.session = {}

    def make_game(self, players: list[str]) -> Game:
        game = Game(game=ZombieDieGame(players))
        self.session[game.id] = game
        return game

    def __getitem__(self, key: str) -> Game:
        return self.session.get(key, None)

    def __iter__(self):
        return iter(self.session.values())
