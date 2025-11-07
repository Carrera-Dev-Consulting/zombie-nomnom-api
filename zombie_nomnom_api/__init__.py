"""
Zombie Nom Nom API - A FastAPI-based GraphQL API for the Zombie Dice Game

This package provides a comprehensive API for playing the Zombie Dice game through both GraphQL and REST endpoints.
The API supports game creation, player management, dice rolling, and score tracking.

Key Features:
    - GraphQL API for game interactions
    - REST endpoints for health checks and authentication
    - Multiple game storage backends (in-memory and MongoDB)
    - OAuth-based authentication system
    - CORS support for web applications
    - Comprehensive test coverage

Modules:
    - server: FastAPI application configuration and middleware
    - app: CLI interface for running the server
    - game: Game state management and storage backends
    - graphql_app: GraphQL schema, resolvers, and dependencies
    - rest_app: REST authentication utilities

.. include:: ../README.md
   :start-line: 2
   :end-before: Contribution
"""

import logging
from pydantic_settings import BaseSettings
from zombie_nomnom_api.game import GameMakerType


class Configs(BaseSettings):
    cors_methods: set[str] = ["*"]
    cors_headers: set[str] = ["*"]
    cors_origins: set[str] = ["*"]
    cors_allow_credentials: bool = True
    log_level: str = "DEBUG"
    game_maker_type: GameMakerType = GameMakerType.memory
    oauth_issuer: str
    oauth_domain: str
    oauth_algorithms: str
    oauth_audience: str


configs = Configs()


logging.basicConfig(level=configs.log_level)
