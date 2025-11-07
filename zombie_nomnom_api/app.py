"""
Module that contains the click entrypoint for our cli interface.

We only handle a handful of configurations for out webserver.
"""

from typing import Any
import re
import click
import uvicorn

from .server import fastapi_app


class HostnameParameter(click.ParamType):
    """
    Custom Click parameter type for validating hostname strings.

    This parameter type ensures that hostname values provided to the CLI
    conform to standard hostname formatting rules using regex validation.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "hostname"

    hostname_format = re.compile(
        r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
    )

    def convert(
        self,
        value: Any,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> Any:
        """
        Convert and validate a hostname parameter value.

        Args:
            value (Any): The value to convert and validate
            param (click.Parameter | None): The Click parameter definition
            ctx (click.Context | None): The Click context

        Returns:
            str: The validated hostname string

        Raises:
            click.BadParameter: If the value is not a valid hostname
        """
        if not isinstance(value, str):
            value = str(value)
        if not self.hostname_format.match(value):
            self.fail("String value is not a valid hostname.")
        return value


@click.command()
@click.option(
    "--port", "-p", type=int, default=5000, help="Port number to bind the server to"
)
@click.option(
    "--host",
    "-h",
    type=HostnameParameter(),
    default="localhost",
    help="Hostname to bind the server to",
)
@click.option(
    "--worker-count",
    "-w",
    type=int,
    default=1,
    help="Number of worker processes to spawn",
)
def main(port: int, host: str, worker_count: int):  # pragma: no cover
    """
    Launch the Zombie Nom Nom API server.

    This is the main CLI entry point for starting the FastAPI server with
    configurable host, port, and worker count settings.

    Args:
        port (int): The port number to bind the server to (default: 5000)
        host (str): The hostname to bind the server to (default: localhost)
        worker_count (int): Number of worker processes (default: 1)
    """
    uvicorn.run(fastapi_app, port=port, host=host, workers=worker_count)


if __name__ == "__main__":  # pragma: no cover
    main()
