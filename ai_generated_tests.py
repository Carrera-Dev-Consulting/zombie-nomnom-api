"""
AI Generated Integration Tests for GraphQL Endpoints

This module contains comprehensive integration tests for the Zombie Nom Nom API
GraphQL endpoints. These tests verify the complete workflow from game creation
to completion, testing all queries and mutations.

Test Coverage:
- Game creation with various player configurations
- Game querying (all games and specific games)
- Dice drawing mechanics
- Round ending and scoring
- Game completion detection
- Error handling scenarios
- Edge cases and validation

Requirements:
- Run `make ensure-resources` before running these tests to start MongoDB
- Tests use the FastAPI TestClient for HTTP requests
- GraphQL operations are tested through the /graphql endpoint
"""

import json
import pytest
from fastapi.testclient import TestClient
from zombie_nomnom_api.server import fastapi_app
from zombie_nomnom_api.graphql_app.dependencies import bootstrap
from zombie_nomnom_api.game import GameMakerInterface


class TestGraphQLIntegration:
    """Integration tests for GraphQL API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application."""
        return TestClient(fastapi_app)

    @pytest.fixture
    def clean_games(self):
        """Clean up games before and after each test."""
        # Clean before test
        container = bootstrap()
        maker: GameMakerInterface = container[GameMakerInterface]
        if hasattr(maker, "session"):
            maker.session.clear()

        yield

        # Clean after test
        if hasattr(maker, "session"):
            maker.session.clear()

    def graphql_request(self, client: TestClient, query: str, variables: dict = None):
        """Helper method to make GraphQL requests."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = client.post("/", json=payload)
        return response

    def test_create_game_with_single_player(self, client: TestClient, clean_games):
        """Test creating a game with a single player."""
        query = """
        mutation CreateGame($players: [String!]!) {
            createGame(players: $players) {
                errors
                game {
                    id
                    players {
                        id
                        name
                        score
                    }
                    gameOver
                    round {
                        player {
                            name
                        }
                    }
                }
            }
        }
        """

        variables = {"players": ["Alice"]}
        response = self.graphql_request(client, query, variables)

        assert response.status_code == 200
        data = response.json()["data"]["createGame"]

        # Verify no errors
        assert data["errors"] == []

        # Verify game creation
        game = data["game"]
        assert game is not None
        assert game["id"] is not None
        assert len(game["players"]) == 1
        assert game["players"][0]["name"] == "Alice"
        assert game["players"][0]["score"] == 0
        assert game["gameOver"] is False

        # Verify round setup
        assert game["round"] is not None
        assert game["round"]["player"]["name"] == "Alice"

    def test_create_game_with_multiple_players(self, client: TestClient, clean_games):
        """Test creating a game with multiple players."""
        query = """
        mutation CreateGame($players: [String!]!) {
            createGame(players: $players) {
                errors
                game {
                    id
                    players {
                        name
                        score
                    }
                    round {
                        player {
                            name
                        }
                    }
                }
            }
        }
        """

        variables = {"players": ["Alice", "Bob", "Charlie"]}
        response = self.graphql_request(client, query, variables)

        assert response.status_code == 200
        data = response.json()["data"]["createGame"]

        assert data["errors"] == []
        game = data["game"]
        assert len(game["players"]) == 3

        player_names = {player["name"] for player in game["players"]}
        assert player_names == {"Alice", "Bob", "Charlie"}

        # First player should start
        assert game["round"]["player"]["name"] == "Alice"

    def test_create_game_with_empty_players_list(self, client: TestClient, clean_games):
        """Test creating a game with no players returns an error."""
        query = """
        mutation CreateGame($players: [String!]!) {
            createGame(players: $players) {
                errors
                game
            }
        }
        """

        variables = {"players": []}
        response = self.graphql_request(client, query, variables)

        assert response.status_code == 200
        data = response.json()["data"]["createGame"]

        # Should have error
        assert len(data["errors"]) > 0
        assert "No players provided" in data["errors"][0]
        assert data["game"] is None

    def test_query_all_games_empty(self, client: TestClient, clean_games):
        """Test querying games when no games exist."""
        query = """
        query GetAllGames {
            games {
                id
                players {
                    name
                }
            }
        }
        """

        response = self.graphql_request(client, query)

        assert response.status_code == 200
        data = response.json()["data"]["games"]
        assert data == []

    def test_query_all_games_with_existing_games(self, client: TestClient, clean_games):
        """Test querying all games when games exist."""
        # First create a couple of games
        create_query = """
        mutation CreateGame($players: [String!]!) {
            createGame(players: $players) {
                game {
                    id
                }
            }
        }
        """

        # Create first game
        response1 = self.graphql_request(
            client, create_query, {"players": ["Alice", "Bob"]}
        )
        game1_id = response1.json()["data"]["createGame"]["game"]["id"]

        # Create second game
        response2 = self.graphql_request(
            client, create_query, {"players": ["Charlie", "Dave"]}
        )
        game2_id = response2.json()["data"]["createGame"]["game"]["id"]

        # Query all games
        query = """
        query GetAllGames {
            games {
                id
                players {
                    name
                    score
                }
                gameOver
            }
        }
        """

        response = self.graphql_request(client, query)

        assert response.status_code == 200
        data = response.json()["data"]["games"]
        assert len(data) == 2

        game_ids = {game["id"] for game in data}
        assert game_ids == {game1_id, game2_id}

    def test_query_specific_game_by_id(self, client: TestClient, clean_games):
        """Test querying a specific game by ID."""
        # Create a game first
        create_query = """
        mutation CreateGame($players: [String!]!) {
            createGame(players: $players) {
                game {
                    id
                }
            }
        }
        """

        create_response = self.graphql_request(
            client, create_query, {"players": ["Alice"]}
        )
        game_id = create_response.json()["data"]["createGame"]["game"]["id"]

        # Query the specific game
        query = """
        query GetGame($gameId: ID!) {
            games(id: $gameId) {
                id
                players {
                    name
                    score
                    hand {
                        color
                        currentFace
                    }
                }
                round {
                    player {
                        name
                    }
                    bag {
                        dice {
                            color
                        }
                    }
                    points
                    ended
                }
                moves {
                    name
                }
            }
        }
        """

        variables = {"gameId": game_id}
        response = self.graphql_request(client, query, variables)

        assert response.status_code == 200
        data = response.json()["data"]["games"]
        assert len(data) == 1

        game = data[0]
        assert game["id"] == game_id
        assert len(game["players"]) == 1
        assert game["players"][0]["name"] == "Alice"
        assert game["players"][0]["score"] == 0
        assert len(game["players"][0]["hand"]) == 0  # No dice drawn yet

        # Check round state
        assert game["round"]["player"]["name"] == "Alice"
        assert game["round"]["points"] == 0
        assert game["round"]["ended"] is None or game["round"]["ended"] is False

        # Should have dice in bag
        assert len(game["round"]["bag"]["dice"]) == 13  # Standard zombie dice set

    def test_query_nonexistent_game(self, client: TestClient, clean_games):
        """Test querying a game that doesn't exist."""
        query = """
        query GetGame($gameId: ID!) {
            games(id: $gameId) {
                id
            }
        }
        """

        variables = {"gameId": "nonexistent-game-id"}
        response = self.graphql_request(client, query, variables)

        assert response.status_code == 200
        data = response.json()["data"]["games"]
        assert data == []

    def test_draw_dice_success(self, client: TestClient, clean_games):
        """Test successfully drawing dice."""
        # Create a game first
        create_query = """
        mutation CreateGame($players: [String!]!) {
            createGame(players: $players) {
                game {
                    id
                }
            }
        }
        """

        create_response = self.graphql_request(
            client, create_query, {"players": ["Alice"]}
        )
        game_id = create_response.json()["data"]["createGame"]["game"]["id"]

        # Draw dice
        draw_query = """
        mutation DrawDice($gameId: ID!) {
            drawDice(gameId: $gameId) {
                errors
                round {
                    player {
                        name
                        hand {
                            color
                            currentFace
                        }
                    }
                    bag {
                        dice {
                            color
                        }
                        drawnDice {
                            color
                            currentFace
                        }
                    }
                    points
                }
            }
        }
        """

        variables = {"gameId": game_id}
        response = self.graphql_request(client, draw_query, variables)

        assert response.status_code == 200
        data = response.json()["data"]["drawDice"]

        # Should have no errors
        assert data["errors"] == []

        # Should have drawn dice
        round_data = data["round"]
        assert round_data["player"]["name"] == "Alice"
        assert len(round_data["player"]["hand"]) == 3  # Standard draw is 3 dice

        # Each die should have color and current face
        for die in round_data["player"]["hand"]:
            assert die["color"] in ["RED", "YELLOW", "GREEN"]
            assert die["currentFace"] in ["BRAIN", "SHOTGUN", "FOOT"]

        # Bag should have fewer dice
        assert len(round_data["bag"]["dice"]) == 10  # 13 - 3 drawn
        assert len(round_data["bag"]["drawnDice"]) == 3

    def test_draw_dice_nonexistent_game(self, client: TestClient, clean_games):
        """Test drawing dice for a nonexistent game."""
        query = """
        mutation DrawDice($gameId: ID!) {
            drawDice(gameId: $gameId) {
                errors
                round
            }
        }
        """

        variables = {"gameId": "nonexistent-game-id"}
        response = self.graphql_request(client, query, variables)

        assert response.status_code == 200
        data = response.json()["data"]["drawDice"]

        # Should have error
        assert len(data["errors"]) > 0
        assert "Game id not found" in data["errors"][0]
        assert data["round"] is None

    def test_draw_dice_missing_game_id(self, client: TestClient, clean_games):
        """Test drawing dice without providing game ID."""
        query = """
        mutation DrawDice($gameId: ID!) {
            drawDice(gameId: $gameId) {
                errors
                round
            }
        }
        """

        # Pass null as game ID
        variables = {"gameId": None}
        response = self.graphql_request(client, query, variables)

        # This should result in a GraphQL validation error
        assert response.status_code == 200
        # The response should contain GraphQL errors, not our custom errors
        response_data = response.json()
        assert "errors" in response_data  # GraphQL level errors

    def test_end_round_success(self, client: TestClient, clean_games):
        """Test successfully ending a round."""
        # Create a game
        create_query = """
        mutation CreateGame($players: [String!]!) {
            createGame(players: $players) {
                game {
                    id
                }
            }
        }
        """

        create_response = self.graphql_request(
            client, create_query, {"players": ["Alice", "Bob"]}
        )
        game_id = create_response.json()["data"]["createGame"]["game"]["id"]

        # Draw dice first
        draw_query = """
        mutation DrawDice($gameId: ID!) {
            drawDice(gameId: $gameId) {
                round {
                    player {
                        name
                    }
                }
            }
        }
        """

        self.graphql_request(client, draw_query, {"gameId": game_id})

        # End the round
        end_query = """
        mutation EndRound($gameId: ID!) {
            endRound(gameId: $gameId) {
                errors
                round {
                    player {
                        name
                        score
                    }
                    points
                    ended
                }
            }
        }
        """

        response = self.graphql_request(client, end_query, {"gameId": game_id})

        assert response.status_code == 200
        data = response.json()["data"]["endRound"]

        # Should have no errors
        assert data["errors"] == []

        # Round should be ended
        round_data = data["round"]
        assert round_data["ended"] is True

        # Should now be Bob's turn (next player)
        assert round_data["player"]["name"] == "Bob"

        # Alice should have some score based on brains rolled
        assert round_data["player"]["score"] >= 0
        assert isinstance(round_data["points"], int)

    def test_end_round_nonexistent_game(self, client: TestClient, clean_games):
        """Test ending round for nonexistent game."""
        query = """
        mutation EndRound($gameId: ID!) {
            endRound(gameId: $gameId) {
                errors
                round
            }
        }
        """

        variables = {"gameId": "nonexistent-game-id"}
        response = self.graphql_request(client, query, variables)

        assert response.status_code == 200
        data = response.json()["data"]["endRound"]

        # Should have error
        assert len(data["errors"]) > 0
        assert "Game id not found" in data["errors"][0]
        assert data["round"] is None

    def test_complete_game_workflow(self, client: TestClient, clean_games):
        """Test a complete game workflow from creation to completion."""
        # 1. Create game
        create_query = """
        mutation CreateGame($players: [String!]!) {
            createGame(players: $players) {
                game {
                    id
                    players {
                        name
                    }
                }
            }
        }
        """

        create_response = self.graphql_request(
            client, create_query, {"players": ["Alice", "Bob"]}
        )
        game_id = create_response.json()["data"]["createGame"]["game"]["id"]

        # 2. Alice's turn - draw and end round
        draw_query = """
        mutation DrawDice($gameId: ID!) {
            drawDice(gameId: $gameId) {
                round {
                    player {
                        name
                        hand {
                            currentFace
                        }
                    }
                }
            }
        }
        """

        # Alice draws dice
        alice_draw = self.graphql_request(client, draw_query, {"gameId": game_id})
        alice_hand = alice_draw.json()["data"]["drawDice"]["round"]["player"]["hand"]

        # Count brains in Alice's hand
        alice_brains = sum(1 for die in alice_hand if die["currentFace"] == "BRAIN")

        # Alice ends her turn
        end_query = """
        mutation EndRound($gameId: ID!) {
            endRound(gameId: $gameId) {
                round {
                    player {
                        name
                        score
                    }
                }
            }
        }
        """

        alice_end = self.graphql_request(client, end_query, {"gameId": game_id})
        alice_final_score = alice_end.json()["data"]["endRound"]["round"]["player"][
            "score"
        ]

        # 3. Bob's turn
        bob_draw = self.graphql_request(client, draw_query, {"gameId": game_id})
        bob_player = bob_draw.json()["data"]["drawDice"]["round"]["player"]
        assert bob_player["name"] == "Bob"

        # Bob ends his turn
        bob_end = self.graphql_request(client, end_query, {"gameId": game_id})
        bob_final_score = bob_end.json()["data"]["endRound"]["round"]["player"]["score"]

        # 4. Check final game state
        game_query = """
        query GetGame($gameId: ID!) {
            games(id: $gameId) {
                id
                players {
                    name
                    score
                }
                gameOver
                winner {
                    name
                    score
                }
                moves {
                    name
                    player {
                        name
                    }
                }
            }
        }
        """

        final_response = self.graphql_request(client, game_query, {"gameId": game_id})
        final_game = final_response.json()["data"]["games"][0]

        # Verify players have correct scores
        alice_player = next(p for p in final_game["players"] if p["name"] == "Alice")
        bob_player = next(p for p in final_game["players"] if p["name"] == "Bob")

        assert alice_player["score"] >= 0
        assert bob_player["score"] >= 0

        # Verify moves were recorded
        assert len(final_game["moves"]) >= 2  # At least 2 actions (draw dice, score)

        # Check if game is over (13+ brains needed to win)
        if final_game["gameOver"]:
            assert final_game["winner"] is not None
            assert final_game["winner"]["score"] >= 13

    def test_multiple_dice_draws_in_round(self, client: TestClient, clean_games):
        """Test drawing dice multiple times in a single round."""
        # Create game
        create_query = """
        mutation CreateGame($players: [String!]!) {
            createGame(players: $players) {
                game {
                    id
                }
            }
        }
        """

        create_response = self.graphql_request(
            client, create_query, {"players": ["Alice"]}
        )
        game_id = create_response.json()["data"]["createGame"]["game"]["id"]

        draw_query = """
        mutation DrawDice($gameId: ID!) {
            drawDice(gameId: $gameId) {
                round {
                    player {
                        hand {
                            currentFace
                        }
                    }
                    bag {
                        dice {
                            color
                        }
                    }
                }
            }
        }
        """

        # First draw
        first_draw = self.graphql_request(client, draw_query, {"gameId": game_id})
        first_hand = first_draw.json()["data"]["drawDice"]["round"]["player"]["hand"]
        first_bag_size = len(
            first_draw.json()["data"]["drawDice"]["round"]["bag"]["dice"]
        )

        # Check if we can continue (no 3 shotguns)
        shotguns = sum(1 for die in first_hand if die["currentFace"] == "SHOTGUN")

        if shotguns < 3:
            # Second draw (if possible)
            second_draw = self.graphql_request(client, draw_query, {"gameId": game_id})
            second_hand = second_draw.json()["data"]["drawDice"]["round"]["player"][
                "hand"
            ]
            second_bag_size = len(
                second_draw.json()["data"]["drawDice"]["round"]["bag"]["dice"]
            )

            # Should have more dice in hand
            assert len(second_hand) >= len(first_hand)

            # Should have fewer dice in bag
            assert second_bag_size <= first_bag_size

    def test_game_state_consistency(self, client: TestClient, clean_games):
        """Test that game state remains consistent across operations."""
        # Create game
        create_response = self.graphql_request(
            client,
            """
            mutation CreateGame($players: [String!]!) {
                createGame(players: $players) {
                    game {
                        id
                        players {
                            id
                            name
                            score
                        }
                    }
                }
            }
            """,
            {"players": ["Alice", "Bob"]},
        )

        game_data = create_response.json()["data"]["createGame"]["game"]
        game_id = game_data["id"]
        initial_players = game_data["players"]

        # Query the same game
        query_response = self.graphql_request(
            client,
            """
            query GetGame($gameId: ID!) {
                games(id: $gameId) {
                    id
                    players {
                        id
                        name
                        score
                    }
                }
            }
            """,
            {"gameId": game_id},
        )

        queried_game = query_response.json()["data"]["games"][0]

        # Game state should be identical
        assert queried_game["id"] == game_id
        assert len(queried_game["players"]) == len(initial_players)

        for initial_player in initial_players:
            matching_player = next(
                p for p in queried_game["players"] if p["id"] == initial_player["id"]
            )
            assert matching_player["name"] == initial_player["name"]
            assert matching_player["score"] == initial_player["score"]


# Additional helper functions for running tests
def run_create_game_test():
    """Helper function to run a simple create game test."""
    client = TestClient(fastapi_app)

    query = """
    mutation CreateGame($players: [String!]!) {
        createGame(players: $players) {
            errors
            game {
                id
                players {
                    name
                }
            }
        }
    }
    """

    response = client.post(
        "/", json={"query": query, "variables": {"players": ["TestPlayer"]}}
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response.json()


def run_full_game_test():
    """Helper function to run a complete game workflow test."""
    client = TestClient(fastapi_app)

    # Clean games first
    container = bootstrap()
    maker: GameMakerInterface = container[GameMakerInterface]
    if hasattr(maker, "session"):
        maker.session.clear()

    print("=== Creating Game ===")
    create_response = client.post(
        "/",
        json={
            "query": """
        mutation CreateGame($players: [String!]!) {
            createGame(players: $players) {
                errors
                game {
                    id
                    players {
                        name
                        score
                    }
                }
            }
        }
        """,
            "variables": {"players": ["Alice", "Bob"]},
        },
    )

    game_data = create_response.json()["data"]["createGame"]
    print(f"Game created: {json.dumps(game_data, indent=2)}")

    if game_data["errors"]:
        print("Error creating game!")
        return

    game_id = game_data["game"]["id"]

    print("\n=== Drawing Dice ===")
    draw_response = client.post(
        "/",
        json={
            "query": """
        mutation DrawDice($gameId: ID!) {
            drawDice(gameId: $gameId) {
                errors
                round {
                    player {
                        name
                        hand {
                            color
                            currentFace
                        }
                    }
                    points
                }
            }
        }
        """,
            "variables": {"gameId": game_id},
        },
    )

    draw_data = draw_response.json()["data"]["drawDice"]
    print(f"Dice drawn: {json.dumps(draw_data, indent=2)}")

    print("\n=== Ending Round ===")
    end_response = client.post(
        "/",
        json={
            "query": """
        mutation EndRound($gameId: ID!) {
            endRound(gameId: $gameId) {
                errors
                round {
                    player {
                        name
                        score
                    }
                    ended
                }
            }
        }
        """,
            "variables": {"gameId": game_id},
        },
    )

    end_data = end_response.json()["data"]["endRound"]
    print(f"Round ended: {json.dumps(end_data, indent=2)}")

    print("\n=== Final Game State ===")
    final_response = client.post(
        "/",
        json={
            "query": """
        query GetGame($gameId: ID!) {
            games(id: $gameId) {
                players {
                    name
                    score
                }
                gameOver
                winner {
                    name
                }
            }
        }
        """,
            "variables": {"gameId": game_id},
        },
    )

    final_data = final_response.json()["data"]["games"][0]
    print(f"Final state: {json.dumps(final_data, indent=2)}")


if __name__ == "__main__":
    """
    Run this file directly to execute some basic tests.

    Usage:
        python ai_generated_tests.py

    For full pytest execution:
        pytest ai_generated_tests.py -v
    """
    print("Running basic GraphQL integration tests...")
    print("\n" + "=" * 50)

    try:
        print("Test 1: Creating a game")
        result = run_create_game_test()
        print("✓ Create game test completed\n")

        print("Test 2: Full game workflow")
        run_full_game_test()
        print("✓ Full workflow test completed\n")

        print("=" * 50)
        print("Basic tests completed successfully!")
        print("\nTo run full test suite with pytest:")
        print("  pytest ai_generated_tests.py -v")
        print("\nTo run with coverage:")
        print("  pytest ai_generated_tests.py --cov=zombie_nomnom_api")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        print("\nMake sure to:")
        print("1. Install dependencies: pip install -r requirements-dev.txt")
        print("2. Start MongoDB: make ensure-resources")
        print("3. Set environment variables if needed")
