# Zombie Nom Nom API - API Reference

## Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://your-production-domain.com`

## Authentication

The API supports JWT-based authentication through OAuth providers. Include the Bearer token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## REST Endpoints

### Health Check

**GET** `/healthz`

Returns the health status of the API.

**Response:**
```json
{
  "o": "k"
}
```

### Version Information

**GET** `/version`

Returns the current API version.

**Response:**
```json
{
  "version": "1.0.0"
}
```

### User Information

**GET** `/me`

Returns information about the authenticated user.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
```json
{
  "sub": "user-id",
  "name": "User Name",
  "email": "user@example.com",
  "scope": "read:games write:games"
}
```

If not authenticated, returns `null`.

## GraphQL API

The primary API interface is GraphQL, available at the root path `/`.

### Schema Overview

```graphql
type Query {
  games(id: ID): [Game!]!
}

type Mutation {
  createGame(players: [String!]!): GameResult!
  drawDice(gameId: ID!): RoundResult!
  endRound(gameId: ID!): RoundResult!
}
```

### Types

#### Game

Represents a Zombie Dice game session.

```graphql
type Game {
  id: ID!
  moves: [Move!]!
  players: [Player!]!
  round: Round
  gameOver: Boolean!
  winner: Player
}
```

**Fields:**
- `id`: Unique game identifier
- `moves`: List of actions taken in the game
- `players`: All players participating in the game
- `round`: Current round state (null if game over)
- `gameOver`: Whether the game has ended
- `winner`: Winning player (only if gameOver is true)

#### Player

Represents a game participant.

```graphql
type Player {
  id: ID!
  name: String!
  score: Int!
  hand: [Die!]!
}
```

**Fields:**
- `id`: Unique player identifier
- `name`: Player display name
- `score`: Current total score (brain count)
- `hand`: Dice currently in the player's hand

#### Die

Represents a single die in the game.

```graphql
type Die {
  sides: [DieFace!]!
  currentFace: DieFace
  color: DieColor!
}
```

**Fields:**
- `sides`: All possible faces on this die
- `currentFace`: The face showing after the last roll (null if not rolled)
- `color`: Die color determining the risk level

#### Round

Represents the current round state.

```graphql
type Round {
  player: Player!
  bag: DieBag!
  points: Int!
  ended: Boolean
}
```

**Fields:**
- `player`: Player currently taking their turn
- `bag`: Current state of the dice bag
- `points`: Points (brains) earned in this round
- `ended`: Whether the round has ended

#### DieBag

Represents the bag containing dice.

```graphql
type DieBag {
  dice: [Die!]!
  drawnDice: [Die!]!
}
```

**Fields:**
- `dice`: Dice still available to draw
- `drawnDice`: Dice that have been drawn this round

#### Move

Represents an action taken in the game.

```graphql
type Move {
  name: String!
  player: Player
}
```

**Fields:**
- `name`: Type of action (e.g., "DrawDice", "Score")
- `player`: Player who performed the action

#### Result Types

**GameResult**
```graphql
type GameResult {
  game: Game
  errors: [String!]!
}
```

**RoundResult**
```graphql
type RoundResult {
  round: Round
  errors: [String!]!
}
```

#### Enums

**DieFace**
```graphql
enum DieFace {
  BRAIN    # Scoring face
  SHOTGUN  # Dangerous face
  FOOT     # Neutral face
}
```

**DieColor**
```graphql
enum DieColor {
  GREEN   # Safe dice (3 brains, 2 feet, 1 shotgun)
  YELLOW  # Medium dice (2 brains, 2 feet, 2 shotguns)
  RED     # Risky dice (1 brain, 2 feet, 3 shotguns)
}
```

## Queries

### Get All Games

Retrieve all games in the system.

```graphql
query GetAllGames {
  games {
    id
    players {
      id
      name
      score
    }
    gameOver
    winner {
      name
      score
    }
  }
}
```

### Get Specific Game

Retrieve a specific game by ID.

```graphql
query GetGame($gameId: ID!) {
  games(id: $gameId) {
    id
    players {
      id
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
        drawnDice {
          color
          currentFace
        }
      }
      points
      ended
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
```

**Variables:**
```json
{
  "gameId": "uuid-string"
}
```

## Mutations

### Create Game

Create a new game with specified players.

```graphql
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
      round {
        player {
          name
        }
      }
    }
  }
}
```

**Variables:**
```json
{
  "players": ["Alice", "Bob", "Charlie"]
}
```

**Success Response:**
```json
{
  "data": {
    "createGame": {
      "errors": [],
      "game": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "players": [
          {
            "id": "player-uuid-1",
            "name": "Alice",
            "score": 0
          },
          {
            "id": "player-uuid-2", 
            "name": "Bob",
            "score": 0
          }
        ],
        "round": {
          "player": {
            "name": "Alice"
          }
        }
      }
    }
  }
}
```

**Error Response:**
```json
{
  "data": {
    "createGame": {
      "errors": ["No players provided"],
      "game": null
    }
  }
}
```

### Draw Dice

Draw dice for the current player.

```graphql
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
      }
      points
    }
  }
}
```

**Variables:**
```json
{
  "gameId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response:**
```json
{
  "data": {
    "drawDice": {
      "errors": [],
      "round": {
        "player": {
          "name": "Alice",
          "hand": [
            {
              "color": "GREEN",
              "currentFace": "BRAIN"
            },
            {
              "color": "YELLOW", 
              "currentFace": "FOOT"
            },
            {
              "color": "RED",
              "currentFace": "SHOTGUN"
            }
          ]
        },
        "bag": {
          "dice": [
            {
              "color": "GREEN"
            }
            // ... remaining dice
          ]
        },
        "points": 1
      }
    }
  }
}
```

### End Round

End the current player's turn and calculate their score.

```graphql
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
```

**Variables:**
```json
{
  "gameId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response:**
```json
{
  "data": {
    "endRound": {
      "errors": [],
      "round": {
        "player": {
          "name": "Alice",
          "score": 3
        },
        "points": 3,
        "ended": true
      }
    }
  }
}
```

## Error Handling

### GraphQL Errors

GraphQL operations return errors in the `errors` field of result objects:

```json
{
  "data": {
    "createGame": {
      "errors": ["No players provided"],
      "game": null
    }
  }
}
```

### Common Error Messages

**Game Operations:**
- `"No game id provided"` - Game ID parameter is missing
- `"Game id not found: {gameId}"` - Game with specified ID doesn't exist
- `"No players provided"` - Empty players array in createGame

**Authentication:**
- `"Not authenticated"` - No valid JWT token provided
- `"User does not have the required 'scope' claim"` - Insufficient permissions

### HTTP Status Codes

**REST Endpoints:**
- `200 OK` - Successful request
- `401 Unauthorized` - Invalid or missing authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Endpoint not found
- `500 Internal Server Error` - Server error

**GraphQL Endpoint:**
- `200 OK` - GraphQL request processed (check response for operation errors)
- `400 Bad Request` - Invalid GraphQL syntax
- `401 Unauthorized` - Authentication required
- `500 Internal Server Error` - Server error

## Rate Limiting

Currently not implemented. Consider implementing rate limiting for production use.

## CORS

The API supports CORS with configurable origins. Default configuration allows all origins (`*`).

**Headers:**
- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Methods`
- `Access-Control-Allow-Headers`
- `Access-Control-Allow-Credentials`

## Game Flow Example

Here's a complete example of creating and playing a game:

### 1. Create Game
```graphql
mutation {
  createGame(players: ["Alice", "Bob"]) {
    errors
    game {
      id
      players {
        name
      }
    }
  }
}
```

### 2. Draw Dice (Alice's turn)
```graphql
mutation {
  drawDice(gameId: "game-id-here") {
    errors
    round {
      player {
        name
        hand {
          color
          currentFace
        }
      }
    }
  }
}
```

### 3. Continue Drawing or End Turn
If Alice got brains and wants to continue:
```graphql
mutation {
  drawDice(gameId: "game-id-here") {
    # ... response
  }
}
```

If Alice wants to score her brains:
```graphql
mutation {
  endRound(gameId: "game-id-here") {
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
```

### 4. Check Game Status
```graphql
query {
  games(id: "game-id-here") {
    gameOver
    winner {
      name
      score
    }
    players {
      name
      score
    }
  }
}
```

## Best Practices

### Query Optimization
- Request only the fields you need
- Use variables for dynamic values
- Consider implementing query complexity analysis for production

### Error Handling
- Always check the `errors` field in mutation responses
- Handle both GraphQL errors and HTTP errors
- Implement retry logic for network failures

### Authentication
- Include authentication tokens when accessing protected resources
- Handle token expiration gracefully
- Store tokens securely

### Real-time Updates
The current API doesn't support real-time updates. Consider polling for game state changes or implementing WebSocket subscriptions for live games.

## SDK Examples

### JavaScript/TypeScript

```typescript
const API_URL = 'http://localhost:5000/graphql';

async function createGame(players: string[]) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      query: `
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
      `,
      variables: { players }
    })
  });
  
  const data = await response.json();
  return data.data.createGame;
}
```

### Python

```python
import requests

API_URL = 'http://localhost:5000/graphql'

def create_game(players: list[str], token: str = None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
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
    
    response = requests.post(
        API_URL,
        json={'query': query, 'variables': {'players': players}},
        headers=headers
    )
    
    return response.json()['data']['createGame']
```

### cURL

```bash
# Create a game
curl -X POST http://localhost:5000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "mutation CreateGame($players: [String!]!) { createGame(players: $players) { errors game { id players { name } } } }",
    "variables": {
      "players": ["Alice", "Bob"]
    }
  }'

# Draw dice
curl -X POST http://localhost:5000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation DrawDice($gameId: ID!) { drawDice(gameId: $gameId) { errors round { player { hand { color currentFace } } } } }",
    "variables": {
      "gameId": "your-game-id"
    }
  }'
```

This API reference provides comprehensive documentation for all available endpoints and operations in the Zombie Nom Nom API.