import pytest

from zombie_nomnom_api.game import GameMaker
from zombie_nomnom_api.graphql_app.dependencies import bootstrap


@pytest.fixture
def di_container():
    return bootstrap()


@pytest.fixture(autouse=True)
def clean_games(di_container):
    maker: GameMaker = di_container[GameMaker]
    maker.session.clear()

    yield

    maker.session.clear()
