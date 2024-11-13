from tests.integration.zombie_nomnom_api.graphql.util import query_api
from zombie_nomnom_api.game import GameMaker


def test_mutation_create_game__when_making_a_game__creates_a_game_with_maker(
    di_container,
    api_client,
):
    maker: GameMaker = di_container[GameMaker]
    original_value = len(list(maker))
    mutation_query = """
    mutation MakeAGame($players: [String!]!){
        createGame(players: $players) {
            errors
            game {
                id
                moves {
                    name
                    player {
                        id
                        name
                    }
                }
                players {
                    id
                    name
                }
            }
        }
    }
    """
    reponse = query_api(
        api_client,
        query=mutation_query,
        variables={"players": ["player one", "player two"]},
    )

    assert reponse.status_code == 200
    assert len(list(maker)) == original_value + 1
    value = reponse.json()["data"]["createGame"]
    assert value["errors"] == []
    assert maker[value["game"]["id"]] is not None
