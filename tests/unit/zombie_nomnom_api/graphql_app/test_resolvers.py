import pytest
from zombie_nomnom_api.game import GameMaker
from zombie_nomnom_api.graphql_app.dependencies import DIContainer
from zombie_nomnom_api.graphql_app.resolvers import games_resolver


@pytest.fixture
def di_container() -> DIContainer:
    return DIContainer()


@pytest.fixture
def game_maker():
    return GameMaker()


def test_games_resolver__when_given_an_id_and_game_exists__returns_list_with_game(
    di_container: DIContainer,
    game_maker: GameMaker,
):
    di_container[GameMaker] = game_maker
    game = game_maker.make_game(["player1", "player2"])
    games = games_resolver(None, None, id=game.id, dependencies=di_container)
    assert len(games) == 1
    assert games[0] == game


def test_games_resolver__when_given_an_id_and_game_does_not_exist__returns_empty_list(
    di_container: DIContainer,
    game_maker: GameMaker,
):
    di_container[GameMaker] = game_maker
    games = games_resolver(
        None, None, id="This game is on fire!!", dependencies=di_container
    )
    assert len(games) == 0


def test_games_resolver__when_not_given_an_id__returns_all_games(
    di_container: DIContainer,
    game_maker: GameMaker,
):
    di_container[GameMaker] = game_maker
    game_maker.make_game(["player1", "player2"])
    game_maker.make_game(["player3", "player4"])

    games = games_resolver(None, None, dependencies=di_container)
    assert len(games) == 2
