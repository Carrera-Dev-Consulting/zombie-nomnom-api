from unittest.mock import patch

import pytest

from zombie_nomnom_api.game import (
    GameMaker,
    GameMakerType,
    MongoGameMaker,
    create_maker,
)


@pytest.fixture
def patch_mongo_client():
    with patch("zombie_nomnom_api.game.MongoClient") as mock:
        yield mock


@pytest.fixture
def patch_mongo_game_maker_config():
    with patch("zombie_nomnom_api.game.MongoGameMakerConfig") as mock:
        yield mock


def test_create_maker__when_given_mongo_type__returns_mongo_maker(
    patch_mongo_client,
    patch_mongo_game_maker_config,
):

    maker = create_maker(GameMakerType.mongo)
    assert isinstance(maker, MongoGameMaker)

    patch_mongo_client.assert_called_once()
    patch_mongo_game_maker_config.assert_called_once()


def test_create_maker__when_given_memory_type__returns_memory_maker():
    maker = create_maker(GameMakerType.memory)
    assert isinstance(maker, GameMaker)
