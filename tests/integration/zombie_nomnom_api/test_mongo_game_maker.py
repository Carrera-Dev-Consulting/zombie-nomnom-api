import pytest

from pymongo import MongoClient
from pymongo.collection import Collection

from zombie_nomnom_api.game import MongoGameMaker


@pytest.fixture(scope="session")
def mongo_client():
    return MongoClient("mongodb://localhost:27017/testing")


@pytest.fixture
def game_collection_name():
    return "games"


@pytest.fixture(scope="session")
def mongo_game_maker(mongo_client: MongoClient):
    return MongoGameMaker(
        mongo_client=mongo_client,
        game_collection_name="games",
    )


@pytest.fixture()
def game_collection(mongo_client: MongoClient, game_collection_name: str):
    game_coll = mongo_client.get_database().get_collection(game_collection_name)
    yield game_coll
    game_coll.drop()


@pytest.mark.mongo
def test_mongo_game_maker__when_making_a_game__saves_it_to_mongo(
    mongo_game_maker: MongoGameMaker,
    game_collection: Collection,
):
    mongo_game_maker.make_game(["player 1"])
    game_collection.find_one()
