"""Main entry point for CLI functions."""

from __future__ import annotations

import logistro
import typer

from .app import server

_logger = logistro.getLogger(__name__)

cli = typer.Typer(help="tetsuya CLI")


@cli.command(name="server")
def _server_start():
    server.start()


@cli.command(name="service")
def _service(name: str):
    # from here, we make a client call to the server
    # are capacity to do that is in _server
    # its a matching endpoint
    pass


def main():
    """Start the cli service."""
    _, remaining = logistro.parser.parse_known_args()
    cli(args=remaining)
