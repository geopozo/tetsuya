from __future__ import annotations

import typer

from . import _server

cli = typer.Typer(help="tetsuya CLI")


@cli.command(name="server")
def server():
    _server.start()


@cli.command()
def service(name: str):
    # from here, we make a client call to the server
    # are capacity to do that is in _server
    # its a matching endpoint
    pass


def main():
    cli()
