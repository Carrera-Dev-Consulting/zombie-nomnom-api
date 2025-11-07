from enum import Enum
from logging import getLogger
import os

from ariadne import (
    EnumType,
    ObjectType,
    SchemaBindable,
    make_executable_schema,
    load_schema_from_path,
)
from typing import TypeVar
from zombie_nomnom import DieColor, Face


_logger = getLogger(__name__)
_registry: dict[str, SchemaBindable] = {}

TRegistry = TypeVar("TRegistry", bound=SchemaBindable)


def register(graphql_type: TRegistry) -> TRegistry:
    """
    Adds bindable type to schema registry for the instantiation of the GraphQL executable schema.

    This function registers GraphQL types (ObjectType, ScalarType, etc.) with the global
    schema registry. The registry is used when building the executable schema to bind
    resolvers and type definitions together.

    Args:
        graphql_type (SchemaBindable): The GraphQL type to register (must implement SchemaBindable)

    Returns:
        SchemaBindable: The same type that was registered, for chaining

    Raises:
        AttributeError: If the type doesn't have a 'name' attribute

    Example:
        >>> @register
        ... Query = ObjectType("Query")
    """
    if not isinstance(graphql_type, SchemaBindable):
        _logger.warning(
            f"Failed to register a non bindable type, Type must implement SchemaBindable from ariadne."
        )
        return

    try:
        key = (
            graphql_type.name
        )  # not defined in base type but all used types will have it.
    except AttributeError:
        _logger.warning(f"Unable to resolve name for schema {graphql_type}")
        return
    if key in _registry:
        _logger.warning(
            f"{key} is already defined as a type skipping duplicate registration."
        )
        return
    _logger.debug(f"Registered type: {key}")
    _registry[key] = graphql_type
    return graphql_type


def register_enum(enum_type: type[Enum], *, name: str = None):
    """
    Shortcut function to register an enum type to the GraphQL type registry.

    This convenience function wraps Python enum types in an Ariadne EnumType
    and registers them with the schema registry for use in GraphQL operations.

    Args:
        enum_type (type[Enum]): The Python enum class to register
        name (str, optional): Alias name for GraphQL. If None, uses the enum's __name__

    Returns:
        EnumType: The registered EnumType instance

    Example:
        >>> from enum import Enum
        >>> class Color(Enum):
        ...     RED = "red"
        ...     BLUE = "blue"
        >>> register_enum(Color)
    """
    return register(EnumType(name or enum_type.__name__, enum_type))


def build_schema():
    """
    Build the executable GraphQL schema from the schema definition and registered types.

    This function combines the GraphQL schema definition file (schema.gql) with all
    registered type bindings to create a fully executable schema that can process
    GraphQL queries and mutations.

    Returns:
        GraphQLSchema: The executable GraphQL schema with bound resolvers

    Raises:
        FileNotFoundError: If the schema.gql file cannot be found
        GraphQLError: If there are issues building the executable schema
    """
    path_to_schema = os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            "schema.gql",
        ),
    )
    _logger.debug(f"Loading schema from path: {path_to_schema}")
    _logger.debug(f"Registered schemas: {list(_registry.keys())}")
    raw_schema = load_schema_from_path(path_to_schema)
    return make_executable_schema(raw_schema, *_registry.values())


Query = register(ObjectType("Query"))
"""
Query type that is used as the entrypoint for reads in grapqhl
"""
Mutation = register(ObjectType("Mutation"))
"""
Mutation type that is used as the entrypoint for writes in grapqhl
"""
GameResource = register(ObjectType("Game"))
"""
Game type that we expose in graphql
"""
Round = register(ObjectType("Round"))
"""
Round type that we expose in graphql
"""
PlayerResource = register(ObjectType("Player"))
"""
Player type that we expose in graphql
"""
DieBagResource = register(ObjectType("DieBag"))
"""
DieBag type that we expose in graphql
"""
DieResource = register(ObjectType("Die"))
"""
Die type that we expose in graphql
"""
Move = register(ObjectType("Move"))
"""
Move type that we expose in graphql
"""

# Register enums for GQL
register_enum(DieColor)
register_enum(Face, name="DieFace")
