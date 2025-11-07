"""
Dependency Injection Container for GraphQL Resolvers

This module provides a simple dependency injection system for managing shared
resources like game makers and game commands. The DIContainer class allows
resolvers to access configured instances without tight coupling.
"""

from functools import cache
from typing import Any

from zombie_nomnom_api import configs
from zombie_nomnom_api.game import GameMakerInterface, create_maker
from zombie_nomnom.engine import DrawDice, Score

_unset = object()


class DIContainer:
    """
    Simple dependency injection container for managing shared instances.

    This container allows registration and retrieval of dependencies by type or string key.
    It supports lazy instantiation where classes are instantiated on first access.

    Attributes:
        _dependencies (dict): Internal storage for registered dependencies
    """

    def __init__(self) -> None:
        """Initialize an empty dependency container."""
        self._dependencies = {}

    def __getitem__(self, key: Any) -> Any:
        """
        Retrieve a dependency by key.

        Args:
            key (Any): The dependency key (usually a type or string)

        Returns:
            Any: The registered dependency instance

        Raises:
            KeyError: If the key is not registered
        """
        value = self.get(key, _unset)
        if value is _unset:
            raise KeyError(key)
        return value

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Register a dependency using bracket notation.

        Args:
            key (Any): The dependency key
            value (Any): The dependency instance or class
        """
        self.register(key, value)

    def register(self, key: type | str, value: Any = None) -> None:
        """
        Register a dependency in the container.

        Args:
            key (type | str): The key to register under (usually a type or string)
            value (Any, optional): The instance or class to register. If None and key is a type,
                                  registers the key as a lazy-instantiated class

        Raises:
            ValueError: If key is a string but no value is provided
        """
        if isinstance(key, str) and not value:
            raise ValueError("value must be provided if key is a string")
        self._dependencies[str(key)] = value or key

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get a dependency with optional default value.

        Args:
            key (Any): The dependency key to look up
            default (Any, optional): Default value if key not found

        Returns:
            Any: The dependency instance or default value
        """
        value = self._dependencies.get(str(key), default)
        if isinstance(value, type):
            # TODO(Milo): Handle dependency injection for anything the constructor needs.
            value = self._dependencies[str(key)] = value()
        return value


@cache
def bootstrap() -> DIContainer:
    """
    Bootstrap the dependency injection container with default dependencies.

    This function creates and configures a DIContainer with all the standard
    dependencies needed by GraphQL resolvers, including the game maker and
    command instances. The container is cached to ensure singleton behavior.

    Returns:
        DIContainer: Configured dependency injection container

    Note:
        This function is cached, so the same container instance will be returned
        on subsequent calls within the same application lifecycle.
    """
    container = DIContainer()
    container[GameMakerInterface] = create_maker(configs.game_maker_type)
    container[DrawDice] = DrawDice()
    container[Score] = Score()
    return container
