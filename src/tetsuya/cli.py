from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import typer
import uvicorn

from ._server import app, is_server_alive, uds_path
from .search_git import SearchGit

if TYPE_CHECKING:
    from ._protocol import Bannin

cli = typer.Typer(help="tetsuya CLI")


def register():
    register: list[Bannin] = [
        SearchGit,
    ]
    return register


@cli.command(name="server")
def server():
    _register = tuple(f() for f in register())
    if not is_server_alive():
        uvicorn.run(app, uds=uds_path())
    else:
        print("Server already running.", file=sys.stderr)  # noqa: T201
        sys.exit(1)


@cli.command()
def service():
    raise ValueError


def main():
    cli()
