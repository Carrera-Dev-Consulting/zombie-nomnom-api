# Zombie Nom Nom API - Technical Documentation

## Overview

The Zombie Nom Nom API is a FastAPI-based GraphQL API that provides a comprehensive interface for playing the Zombie Dice game. The API supports game creation, player management, dice rolling, and score tracking through both GraphQL and REST endpoints.

## Architecture

### Core Components

The API is structured into several key modules:

1. **Main Application** (`zombie_nomnom_api/`)
   - Server configuration and middleware
   - CLI interface for deployment
   - Configuration management

2. **Game Engine** (`zombie_nomnom_api/game.py`)
   - Game state management
   - Multiple storage backends (in-memory, MongoDB)
   - Game session handling

3. **GraphQL API** (`zombie_nomnom_api/graphql_app/`)
   - Schema definition and type binding
   - Query and mutation resolvers
   - Dependency injection system

4. **REST API** (`zombie_nomnom_api/rest_app/`)
   - JWT authentication utilities
   - OAuth integration

### Key Features

- **GraphQL API**: Primary interface for game interactions
- **REST Endpoints**: Health checks, version info, and authentication
- **Multiple Storage Backends**: In-memory for development, MongoDB for production
- **OAuth Authentication**: JWT-based user authentication and authorization
- **CORS Support**: Configurable cross-origin resource sharing
- **Comprehensive Testing**: Unit and integration test coverage

## Module Documentation

### Main Application (`__init__.py`)

The main module provides configuration management and package initialization. It includes:

- **Configs Class**: Pydantic-based settings management for CORS, logging, and OAuth
- **Global Configuration**: Centralized configuration instance
- **Package Metadata**: Version information and module exports

### Server (`server.py`)

The FastAPI server configuration includes:

- **CORS Middleware**: Configurable cross-origin request handling
- **Authentication Middleware**: JWT token verification and user hydration
- **Health Endpoints**: Status and version information
- **GraphQL Integration**: Mounts GraphQL app at root path

Key endpoints:
- `GET /healthz` - Health check
- `GET /version` - API version information
- `GET /me` - Authenticated user information
- `POST /graphql` - GraphQL query/mutation endpoint

### CLI Interface (`app.py`)

Command-line interface for running the server:

```bash
zombie-nomnom-api --host localhost --port 5000 --worker-count 1
```

Features:
- **Hostname Validation**: Custom Click parameter type for hostname validation
- **Configurable Deployment**: Port, host, and worker count configuration
- **Uvicorn Integration**: ASGI server with production-ready settings

### Game Management (`game.py`)

Core game state management with pluggable storage backends:

#### Game Class
Wrapper for ZombieDieGame instances with unique identification:
- **Unique IDs**: UUID-based game session tracking
- **Serialization**: JSON serialization for persistent storage
- **Game Logic Integration**: Wraps the core zombie-nomnom game engine

#### Storage Backends

**InMemoryGameMaker**
- Development and testing focused storage
- Fast access with dictionary-based storage
- Non-persistent (lost on restart)

**MongoGameMaker**
- Production-ready persistent storage
- MongoDB integration with configurable collections
- Automatic serialization/deserialization

#### GameMakerInterface Protocol
Defines the contract for game storage implementations:
- `make_game(players: list[str]) -> Game`
- `__getitem__(key: str) -> Game`
- `__iter__()` - Iterator over all games

### GraphQL API

#### Schema Definition (`graphql_app/schema.py`)

Type registration system for GraphQL schema binding:

- **Type Registry**: Global registry for GraphQL type bindings
- **Automatic Registration**: Decorator-based type registration
- **Enum Support**: Python enum to GraphQL enum conversion
- **Schema Building**: Combines .gql file with registered types

#### Resolvers (`graphql_app/resolvers.py`)

GraphQL query and mutation handlers:

**Query Resolvers:**
- `games(id: ID)` - Retrieve games by ID or all games

**Mutation Resolvers:**
- `createGame(players: [String!]!)` - Create new game with players
- `drawDice(gameId: ID!)` - Draw dice for current player
- `endRound(gameId: ID!)` - End current player's turn and calculate score

**Field Resolvers:**
- Game state transformation (game over, winner, rounds)
- Player information (score, hand, name)
- Die and bag state (colors, faces, drawn dice)

#### Dependency Injection (`graphql_app/dependencies.py`)

Simple DI container for resolver dependencies:

- **DIContainer**: Lightweight dependency injection
- **Lazy Instantiation**: Classes instantiated on first access
- **Bootstrap Function**: Cached container setup with standard dependencies

### REST Authentication (`rest_app/authentication.py`)

JWT token verification for OAuth integration:

#### VerifyToken Class
- **JWKS Integration**: Automatic key retrieval from OAuth provider
- **Token Validation**: Signature, expiration, audience, and issuer verification
- **Claims Verification**: Custom scope and permission checking
- **Error Handling**: Standardized error responses

#### Security Integration
- **FastAPI HTTPBearer**: Bearer token extraction from headers
- **Cached Verifier**: Singleton pattern for performance optimization

## GraphQL Schema

### Types

**Game**
- `id: ID!` - Unique game identifier
- `moves: [Move!]!` - List of game actions
- `players: [Player!]!` - Game participants
- `round: Round` - Current round state
- `gameOver: Boolean!` - Game completion status
- `winner: Player` - Winning player (if game over)

**Player**
- `id: ID!` - Unique player identifier
- `name: String!` - Player display name
- `score: Int!` - Current total score
- `hand: [Die!]!` - Dice currently in hand

**Die**
- `sides: [DieFace!]!` - All possible die faces
- `currentFace: DieFace` - Result of last roll
- `color: DieColor!` - Die color (RED, YELLOW, GREEN)

**Round**
- `player: Player!` - Player taking the round
- `bag: DieBag!` - Current dice bag state
- `points: Int!` - Points earned this round
- `ended: Boolean` - Round completion status

### Queries

```graphql
query GetAllGames {
  games {
    id
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

query GetGameById($id: ID!) {
  games(id: $id) {
    id
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

### Mutations

```graphql
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

mutation DrawDice($gameId: ID!) {
  drawDice(gameId: $gameId) {
    errors
    round {
      player {
        hand {
          currentFace
        }
      }
    }
  }
}

mutation EndRound($gameId: ID!) {
  endRound(gameId: $gameId) {
    errors
    round {
      player {
        score
      }
      ended
    }
  }
}
```

## Configuration

### Environment Variables

**CORS Configuration:**
- `CORS_ORIGINS` - Allowed origins (default: "*")
- `CORS_ALLOW_CREDENTIALS` - Allow credentials (default: True)
- `CORS_METHODS` - Allowed methods (default: "*")
- `CORS_HEADERS` - Allowed headers (default: "*")

**Logging:**
- `LOG_LEVEL` - Logging level (default: "DEBUG")

**Game Storage:**
- `GAME_MAKER_TYPE` - Storage backend ("memory" or "mongo")

**MongoDB Configuration:**
- `MONGO_CONNECTION` - MongoDB connection string
- `GAME_COLLECTION_NAME` - Collection name for games

**OAuth Configuration:**
- `OAUTH_ISSUER` - JWT issuer URL
- `OAUTH_DOMAIN` - OAuth provider domain
- `OAUTH_ALGORITHMS` - Supported JWT algorithms
- `OAUTH_AUDIENCE` - Expected token audience

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run with development settings
python -m zombie_nomnom_api

# Run with custom configuration
zombie-nomnom-api --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# Build container
docker build -t zombie-nomnom-api .

# Run with environment variables
docker run -p 5000:5000 \
  -e GAME_MAKER_TYPE=mongo \
  -e MONGO_CONNECTION=mongodb://mongo:27017/zombie_nomnom \
  zombie-nomnom-api
```

### Production Considerations

1. **Database**: Use MongoDB for persistent storage
2. **Authentication**: Configure OAuth provider settings
3. **CORS**: Restrict origins for security
4. **Logging**: Set appropriate log levels
5. **Monitoring**: Implement health check monitoring
6. **Scaling**: Use multiple worker processes

## API Usage Examples

### Creating and Playing a Game

1. **Create a new game:**
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

2. **Draw dice for current player:**
```graphql
mutation {
  drawDice(gameId: "game-uuid-here") {
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

3. **End the round:**
```graphql
mutation {
  endRound(gameId: "game-uuid-here") {
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

4. **Check game status:**
```graphql
query {
  games(id: "game-uuid-here") {
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

## Testing

The API includes comprehensive test coverage:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows
- **GraphQL Tests**: Validate schema and resolvers
- **Authentication Tests**: Verify JWT token handling

### Running Tests

```bash
# Unit tests only
make unit-test

# Integration tests (requires MongoDB)
make ensure-resources
make int-test

# All tests with coverage
make all-test
```

## Error Handling

The API uses consistent error handling patterns:

### GraphQL Errors
- Mutations return `errors` arrays with descriptive messages
- Successful operations return empty error arrays
- Invalid game IDs and missing parameters are handled gracefully

### REST Errors
- Standard HTTP status codes
- JSON error responses with `status` and `message` fields
- Authentication errors return 401/403 as appropriate

### Common Error Scenarios
1. **Game Not Found**: Invalid game ID in mutations
2. **No Players**: Creating game without players
3. **Authentication Failed**: Invalid or expired JWT tokens
4. **Database Errors**: MongoDB connection issues
5. **Validation Errors**: Invalid input parameters

## Security Considerations

1. **JWT Validation**: Full signature and claims verification
2. **CORS Configuration**: Restrict origins in production
3. **Input Validation**: GraphQL schema validation
4. **Error Messages**: Avoid leaking sensitive information
5. **Rate Limiting**: Consider implementing for production use

## Performance Optimization

1. **Cached Dependencies**: Singleton pattern for expensive resources
2. **Connection Pooling**: MongoDB connection reuse
3. **Lazy Loading**: On-demand dependency instantiation
4. **GraphQL Efficiency**: Field-level resolvers prevent over-fetching

## Future Enhancements

1. **Real-time Updates**: WebSocket support for live games
2. **Player Matchmaking**: Automatic player pairing
3. **Game History**: Persistent move history and statistics
4. **Admin Panel**: Game management interface
5. **Rate Limiting**: Request throttling for production
6. **Metrics**: Performance and usage monitoring