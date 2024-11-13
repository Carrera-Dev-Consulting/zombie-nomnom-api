from logging import getLogger
import os

from ariadne import (
    ObjectType,
    SchemaBindable,
    make_executable_schema,
    load_schema_from_path,
)
import zombie_nomnom_api


logger = getLogger(__name__)
registry: dict[str, SchemaBindable] = {}


def register(graphql_type: SchemaBindable):
    if not isinstance(graphql_type, SchemaBindable):
        logger.warning(
            f"Failed to register a non bindable type, Type must implement SchemaBindable from ariadne."
        )
        return

    try:
        key = (
            graphql_type.name
        )  # not defined in base type but all used types will have it.
    except AttributeError:
        logger.warning(f"Unable to resolve name for schema {graphql_type}")
        return
    if key in registry:
        logger.warning(
            f"{key} is already defined as a type skipping duplicate registration."
        )
        return
    logger.debug(f"Registered type: {key}")
    registry[key] = graphql_type


def build_schema():
    path_to_schema = os.path.normpath(
        os.path.join(
            os.path.dirname(zombie_nomnom_api.__file__),
            "graphql_app",
            "schema.gql",
        ),
    )
    logger.debug(f"Loading schema from path: {path_to_schema}")
    logger.debug(f"Registered schemas: {list(registry.keys())}")
    raw_schema = load_schema_from_path(path_to_schema)
    return make_executable_schema(raw_schema, *registry.values())


class ObjectTypeBuilder:
    """
    Builder for the different schema types
    that registers itself in the global
    map using the native ariadne ObjectType bindable.
    """

    def __init__(self, name: str) -> None:
        self._instance = ObjectType(name)
        register(self._instance)

    def __getattr__(self, name: str):
        return self._instance.field(name)


Query = ObjectTypeBuilder("Query")
Mutation = ObjectTypeBuilder("Mutation")
