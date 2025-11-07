from enum import Enum
from typing import Protocol, runtime_checkable
import uuid

from pydantic_settings import BaseSettings
from pymongo.collection import Collection
from pymongo import MongoClient

from zombie_nomnom import ZombieDieGame
from zombie_nomnom.engine.serialization import format_to_json_dict, parse_game_json_dict


class Game:
    """
    Wrapper class for ZombieDieGame instances with unique identification.

    This class provides a container for the core zombie dice game logic
    along with a unique identifier for tracking game sessions across
    different storage backends.

    Attributes:
        game (ZombieDieGame): The core game logic instance
        id (str): Unique identifier for this game session
    """

    game: ZombieDieGame
    id: str

    def __init__(self, *, game: ZombieDieGame, id: str = None) -> None:
        """
        Initialize a new Game instance.

        Args:
            game (ZombieDieGame): The core game logic instance
            id (str, optional): Unique identifier. If None, generates a new UUID
        """
        self.game = game
        self.id = id or str(uuid.uuid4())

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Game) and self.id == value.id

    @classmethod
    def from_dict(cls, game_data: dict) -> "Game":
        """
        Create a Game instance from a dictionary representation.

        Args:
            game_data (dict): Dictionary containing game state and ID

        Returns:
            Game: New Game instance deserialized from the dictionary
        """
        id = game_data.pop("id", None)
        game = parse_game_json_dict(game_data["game"])
        return cls(game=game, id=id)

    def to_dict(self) -> dict:
        """
        Convert the Game instance to a dictionary representation.

        Returns:
            dict: Dictionary containing the game state and ID for serialization
        """
        return {
            "id": self.id,
            "game": format_to_json_dict(self.game),
        }


@runtime_checkable
class GameMakerInterface(Protocol):
    """
    Defines the methods that are used by game makers to create and load games currently.
    """

    def make_game(self, players: list[str]) -> Game: ...

    def __getitem__(self, key: str) -> Game: ...

    def __iter__(self): ...


class InMemoryGameMaker:
    """
    In-memory implementation of GameMakerInterface.

    This implementation stores all game instances in memory using a dictionary.
    Game data will be lost when the application restarts, making this suitable
    for development and testing environments.

    Attributes:
        session (dict): Dictionary storing Game instances by their ID
    """

    def __init__(self) -> None:
        """Initialize an empty in-memory game storage."""
        self.session = {}

    def make_game(self, players: list[str]) -> Game:
        """
        Create a new game with the specified players.

        Args:
            players (list[str]): List of player names for the new game

        Returns:
            Game: Newly created game instance
        """
        game = Game(game=ZombieDieGame(players))
        self.session[game.id] = game
        return game

    def __getitem__(self, key: str) -> Game:
        """
        Retrieve a game by its ID.

        Args:
            key (str): The game ID to lookup

        Returns:
            Game | None: The game instance if found, None otherwise
        """
        return self.session.get(key, None)

    def __iter__(self):
        """
        Iterate over all stored games.

        Returns:
            Iterator[Game]: Iterator over all game instances
        """
        return iter(self.session.values())


class MongoGameMaker:
    """
    MongoDB implementation of GameMakerInterface.

    This implementation persists game instances in a MongoDB collection,
    providing durable storage that survives application restarts. Suitable
    for production environments requiring persistent game state.

    Attributes:
        mongo_client (MongoClient): The MongoDB client connection
        game_collection (Collection): The MongoDB collection for storing games
    """

    def __init__(self, mongo_client: MongoClient, game_collection_name) -> None:
        """
        Initialize MongoDB game storage.

        Args:
            mongo_client (MongoClient): Connected MongoDB client
            game_collection_name (str): Name of the collection to store games
        """
        self.mongo_client = mongo_client
        self.game_collection: Collection = mongo_client.get_database().get_collection(
            game_collection_name
        )

    def make_game(self, players: list[str]) -> Game:
        """
        Create a new game with the specified players and persist it to MongoDB.

        Args:
            players (list[str]): List of player names for the new game

        Returns:
            Game: Newly created and persisted game instance
        """
        game = Game(game=ZombieDieGame(players))
        self.game_collection.insert_one(game.to_dict())
        return game

    def load_game(self, game_id: str) -> Game | None:
        """
        Load a game from MongoDB by its ID.

        Args:
            game_id (str): The unique game identifier

        Returns:
            Game | None: The game instance if found, None otherwise
        """
        game_data = self.game_collection.find_one({"id": game_id})
        if game_data is None:
            return None

        game = Game.from_dict(game_data)
        return game

    def get_all_games(self) -> list[Game]:
        """
        Retrieve all games from the MongoDB collection.

        Returns:
            list[Game]: List of all game instances in the database
        """
        games_data = self.game_collection.find()
        games = [Game.from_dict(game_data) for game_data in games_data]
        return games

    def __getitem__(self, key: str) -> Game:
        """
        Retrieve a game by its ID (implements GameMakerInterface).

        Args:
            key (str): The game ID to lookup

        Returns:
            Game | None: The game instance if found, None otherwise
        """
        return self.load_game(key)

    def __iter__(self):
        """
        Iterate over all games in the MongoDB collection.

        Returns:
            Iterator[Game]: Iterator over all game instances in the database
        """
        return iter(self.get_all_games())


class MongoGameMakerConfig(BaseSettings):
    """Environment Config settings for MongoGameMakers to allow us to not have to
    need mongo connection details unless we are loading the mongo engine.
    """

    mongo_connection: str = "mongodb://localhost:27017/zombie_nomnom"
    """
    Full mongo connection string uri ex. mongodb://localhost:27017/zombie_nomnom
    """
    game_collection_name: str = "games"
    """
    Name of the collection where we store game data.
    """


class GameMakerType(str, Enum):
    """
    Enum for the supported types of game makers we have implemented.
    """

    memory = "memory"
    mongo = "mongo"


def create_maker(kind: GameMakerType) -> GameMakerInterface:
    """Translates the game maker type to the implementation of the GameMakerInterface

    **Parameters**
    - kind (GameMakerType): The kind of game maker we want.

    **Raises**
    - ValueError: Given a GameMakerType that we do not have mapped.

    **Returns**
    - GameMakerInterface: GameMaker implementation
    """
    if kind == GameMakerType.mongo:
        config = MongoGameMakerConfig()
        return MongoGameMaker(
            game_collection_name=config.game_collection_name,
            mongo_client=MongoClient(config.mongo_connection),
        )
    elif kind == GameMakerType.memory:
        return InMemoryGameMaker()
    raise ValueError(f"Invalid game maker type: {kind}")
