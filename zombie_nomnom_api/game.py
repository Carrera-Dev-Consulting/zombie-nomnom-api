import uuid
from zombie_nomnom import ZombieDieGame
from zombie_nomnom.engine.serialization import format_to_json_dict, parse_game_json_dict

from zombie_nomnom_api.db.client import MongoClient


class Game:
    game: ZombieDieGame
    id: str

    def __init__(self, *, game: ZombieDieGame, id: str = None) -> None:
        self.game = game
        self.id = id or str(uuid.uuid4())

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Game) and self.id == value.id

    def from_dict(cls, game_data: dict) -> "Game":
        id = game_data.pop("id", None)
        game = parse_game_json_dict(game_data["game"])
        return cls(game=game, id=id)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "game": format_to_json_dict(self.game),
        }


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


class MongoGameMaker:
    def __init__(self, mongo_client: MongoClient, game_collection) -> None:
        self.mongo_client = mongo_client
        self.game_collection = game_collection

    def make_game(self, players: list[str]) -> Game:
        game = Game(game=ZombieDieGame(players))
        self.game_collection.insert_one(game.to_dict())
        return game

    def load_game(self, game_id: str) -> Game:
        game_data = self.game_collection.find_one({"id": game_id})
        game = Game.from_dict(game_data)
        return game

    def get_all_games(self) -> list[Game]:
        games_data = self.game_collection.find()
        games = [Game.from_dict(game_data) for game_data in games_data]
        return games

    def __getitem__(self, key: str) -> Game:
        return self.load_game(key)

    def __iter__(self):
        return iter(self.get_all_games())
