"""
GraphQL Application Configuration

This module creates the main GraphQL application instance using Ariadne.
The application combines the schema definition with resolver implementations
to provide a complete GraphQL API for the Zombie Dice game.
"""

from ariadne.asgi import GraphQL
from .schema import build_schema
import zombie_nomnom_api.graphql_app.resolvers

# TODO(Milo): Make this configurable somehow.
graphql_app = GraphQL(build_schema(), debug=True)
"""GraphQL ASGI application instance configured with the Zombie Dice schema and resolvers."""
