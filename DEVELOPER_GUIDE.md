# Zombie Nom Nom API - Developer Guide

## Getting Started

This guide will help you set up the development environment and understand the codebase structure for contributing to the Zombie Nom Nom API.

## Prerequisites

- Python 3.10 or higher
- MongoDB (for integration tests and production storage)
- Docker (optional, for containerized development)
- Git

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Carrera-Dev-Consulting/zombie-nomnom-api.git
cd zombie-nomnom-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
pip install -r requirements-dev.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Development settings
LOG_LEVEL=DEBUG
GAME_MAKER_TYPE=memory

# OAuth settings (required for authentication)
OAUTH_DOMAIN=your-auth0-domain.auth0.com
OAUTH_ISSUER=https://your-auth0-domain.auth0.com/
OAUTH_AUDIENCE=your-api-audience
OAUTH_ALGORITHMS=RS256

# MongoDB settings (for integration tests)
MONGO_CONNECTION=mongodb://localhost:27017/zombie_nomnom_test
GAME_COLLECTION_NAME=games
```

### 5. Start Development Server

```bash
python -m zombie_nomnom_api
# Or using the CLI
zombie-nomnom-api --host localhost --port 5000
```

The API will be available at:
- GraphQL Playground: http://localhost:5000/
- Health Check: http://localhost:5000/healthz
- Version Info: http://localhost:5000/version

## Code Structure

### Project Layout

```
zombie_nomnom_api/
├── __init__.py              # Package initialization and configuration
├── app.py                   # CLI interface and application entry point
├── server.py                # FastAPI server configuration
├── game.py                  # Game state management and storage backends
├── graphql_app/             # GraphQL implementation
│   ├── __init__.py
│   ├── app.py              # GraphQL application setup
│   ├── schema.py           # GraphQL schema definition and registration
│   ├── schema.gql          # GraphQL schema definition file
│   ├── resolvers.py        # Query and mutation resolvers
│   └── dependencies.py     # Dependency injection container
└── rest_app/               # REST API utilities
    ├── __init__.py
    └── authentication.py   # JWT authentication and verification
```

### Key Design Patterns

#### 1. Protocol-Based Interfaces

The codebase uses Python protocols to define interfaces, particularly for storage backends:

```python
@runtime_checkable
class GameMakerInterface(Protocol):
    def make_game(self, players: list[str]) -> Game: ...
    def __getitem__(self, key: str) -> Game: ...
    def __iter__(self): ...
```

This allows for easy substitution of storage implementations without changing dependent code.

#### 2. Dependency Injection

The GraphQL resolvers use a simple dependency injection container:

```python
@cache
def bootstrap() -> DIContainer:
    container = DIContainer()
    container[GameMakerInterface] = create_maker(configs.game_maker_type)
    container[DrawDice] = DrawDice()
    container[Score] = Score()
    return container
```

This pattern makes testing easier and keeps resolvers decoupled from specific implementations.

#### 3. Factory Pattern

Game storage backends are created using a factory function:

```python
def create_maker(kind: GameMakerType) -> GameMakerInterface:
    if kind == GameMakerType.mongo:
        config = MongoGameMakerConfig()
        return MongoGameMaker(...)
    elif kind == GameMakerType.memory:
        return InMemoryGameMaker()
```

#### 4. Decorator-Based Registration

GraphQL types are registered using decorators:

```python
@register
Query = ObjectType("Query")

@register
Mutation = ObjectType("Mutation")
```

## Development Workflow

### Running Tests

The project uses pytest with comprehensive test coverage:

```bash
# Run unit tests only
make unit-test

# Run integration tests (requires MongoDB)
make ensure-resources  # Starts MongoDB if needed
make int-test

# Run all tests with coverage
make all-test

# Run database-specific tests
make db-test
```

### Code Quality

#### Formatting
The project uses Black for code formatting:

```bash
# Format code
make format

# Check formatting
make lint
```

#### Testing Strategy

1. **Unit Tests** (`tests/unit/`): Test individual components in isolation
2. **Integration Tests** (`tests/integration/`): Test complete workflows
3. **Fixtures**: Shared test utilities and mock objects

Example test structure:
```python
def test_create_game_resolver__when_players_provided__returns_new_game_instance():
    # Arrange
    di_container[GameMakerInterface] = game_maker
    
    # Act
    response = create_game_resolver(None, None, players=["Player One"], dependencies=di_container)
    
    # Assert
    assert response["errors"] == []
    assert response["game"]
```

### Adding New Features

#### 1. Adding GraphQL Fields

1. Update `schema.gql`:
```graphql
type Player {
    id: ID!
    name: String!
    score: Int!
    # Add new field
    totalGames: Int!
}
```

2. Add resolver in `resolvers.py`:
```python
@PlayerResource.field("totalGames")
def player_total_games_resolver(player: Player, _):
    # Implementation here
    return calculate_total_games(player)
```

3. Add tests:
```python
def test_player_total_games_resolver():
    # Test implementation
    pass
```

#### 2. Adding New Mutations

1. Update `schema.gql`:
```graphql
type Mutation {
    # Existing mutations...
    
    # New mutation
    resetGame(gameId: ID!): GameResult!
}
```

2. Add resolver:
```python
@Mutation.field("resetGame")
def reset_game_resolver(_, __, gameId: str, dependencies: DIContainer = bootstrap()):
    # Implementation
    pass
```

3. Add integration tests:
```python
def test_mutation_reset_game():
    # Test the complete workflow
    pass
```

#### 3. Adding New Storage Backends

1. Implement the `GameMakerInterface`:
```python
class RedisGameMaker:
    def make_game(self, players: list[str]) -> Game:
        # Implementation
        pass
    
    def __getitem__(self, key: str) -> Game:
        # Implementation
        pass
    
    def __iter__(self):
        # Implementation
        pass
```

2. Add to the factory:
```python
class GameMakerType(str, Enum):
    memory = "memory"
    mongo = "mongo"
    redis = "redis"  # New type

def create_maker(kind: GameMakerType) -> GameMakerInterface:
    # Add new case
    elif kind == GameMakerType.redis:
        return RedisGameMaker()
```

3. Add configuration and tests.

### GraphQL Development

#### Schema Development
The GraphQL schema is defined in `schema.gql`. Key principles:

1. **Type Safety**: Use strong typing with required fields where appropriate
2. **Error Handling**: Return error arrays in mutation results
3. **Consistency**: Follow established naming conventions

#### Resolver Development
Resolvers should:

1. **Validate Input**: Check for required parameters
2. **Handle Errors**: Return structured error responses
3. **Use Dependency Injection**: Access services through the DI container
4. **Be Testable**: Keep logic separate from GraphQL concerns

Example resolver pattern:
```python
@Mutation.field("exampleMutation")
def example_mutation_resolver(_, __, param: str, dependencies: DIContainer = bootstrap()):
    # Validate input
    if not param:
        return {"errors": ["Parameter required"], "result": None}
    
    # Get dependencies
    service = dependencies[SomeService]
    
    # Execute logic
    try:
        result = service.do_something(param)
        return {"errors": [], "result": result}
    except Exception as e:
        return {"errors": [str(e)], "result": None}
```

### Authentication Development

The authentication system uses JWT tokens with OAuth providers. Key components:

#### Token Verification
The `VerifyToken` class handles:
- JWKS key retrieval
- Token signature verification
- Claims validation
- Scope and permission checking

#### Middleware Integration
The `hydrate_user` middleware:
- Extracts tokens from requests
- Verifies tokens using `VerifyToken`
- Adds user information to request state
- Handles authentication errors

### Configuration Management

Configuration uses Pydantic settings with environment variable support:

```python
class Configs(BaseSettings):
    cors_methods: set[str] = ["*"]
    cors_headers: set[str] = ["*"]
    # ... other settings
    
    class Config:
        env_file = ".env"
```

Adding new configuration:
1. Add field to `Configs` class
2. Update environment documentation
3. Add tests for configuration validation

## Debugging

### Common Issues

#### 1. GraphQL Schema Errors
- Check that all types are registered with `@register`
- Verify resolver function names match schema field names
- Ensure schema.gql syntax is valid

#### 2. Authentication Issues
- Verify OAuth configuration variables
- Check JWKS endpoint accessibility
- Validate token format and claims

#### 3. Database Connection Issues
- Ensure MongoDB is running for integration tests
- Check connection string format
- Verify database permissions

### Debugging Tools

#### 1. GraphQL Playground
Access at http://localhost:5000/ when running the development server.

#### 2. Logging
Set `LOG_LEVEL=DEBUG` for verbose logging:
```python
import logging
logging.basicConfig(level="DEBUG")
```

#### 3. VS Code Configuration
The project includes VS Code configuration for debugging:
- Python debugger setup
- Test discovery configuration
- Launch configurations

## Contributing Guidelines

### Code Style
- Use Black for formatting
- Follow PEP 8 conventions
- Write descriptive docstrings
- Use type hints where possible

### Commit Messages
Follow conventional commit format:
- `feat: add new GraphQL mutation`
- `fix: resolve authentication error`
- `docs: update API documentation`
- `test: add integration tests for game creation`

### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Update documentation if needed
4. Ensure all tests pass
5. Submit pull request with description

### Testing Requirements
- All new features must include tests
- Maintain or improve test coverage
- Integration tests for user-facing features
- Unit tests for individual components

## Performance Considerations

### Caching
- Use `@cache` decorator for expensive operations
- Implement singleton pattern for shared resources
- Consider Redis for distributed caching

### Database Optimization
- Use connection pooling for MongoDB
- Implement pagination for large result sets
- Consider indexing for frequently queried fields

### GraphQL Optimization
- Implement field-level resolvers
- Use DataLoader pattern for N+1 queries
- Consider query complexity analysis

## Security Best Practices

### Authentication
- Always verify JWT signatures
- Validate all claims (audience, issuer, expiration)
- Use HTTPS in production
- Implement proper error handling

### Input Validation
- Use GraphQL schema validation
- Sanitize database queries
- Validate file uploads if added
- Implement rate limiting

### Error Handling
- Don't leak sensitive information in errors
- Log security events
- Use structured error responses
- Implement proper exception handling

## Deployment

### Environment-Specific Configuration

#### Development
```env
LOG_LEVEL=DEBUG
GAME_MAKER_TYPE=memory
CORS_ORIGINS=["http://localhost:3000"]
```

#### Production
```env
LOG_LEVEL=INFO
GAME_MAKER_TYPE=mongo
CORS_ORIGINS=["https://yourdomain.com"]
MONGO_CONNECTION=mongodb://prod-mongo:27017/zombie_nomnom
```

### Container Deployment
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install .
EXPOSE 5000
ENTRYPOINT ["zombie-nomnom-api", "--port", "5000", "--host", "0.0.0.0"]
```

### Health Checks
Implement health checks for:
- Database connectivity
- External service availability
- Application startup status

## Monitoring and Observability

### Logging
Structure logs with consistent format:
```python
logger.info("Game created", extra={
    "game_id": game.id,
    "player_count": len(players),
    "timestamp": datetime.utcnow()
})
```

### Metrics
Consider implementing:
- Request/response times
- Error rates
- Game creation statistics
- User authentication metrics

### Tracing
For distributed deployments:
- Request correlation IDs
- Distributed tracing with OpenTelemetry
- Performance monitoring

This developer guide should help you get started with contributing to the Zombie Nom Nom API. For specific questions or issues, please refer to the issue tracker or contact the maintainers.