"""core provides the globals that every interface needs."""

import cli_tree
import typer
from fastapi import FastAPI

from ._serializer import ORJSONUtcResponse

cli = typer.Typer(name="Tetsuya CLI")


@cli.callback()
def _cb(help_tree=cli_tree.help_tree_option):
    pass


daemon = FastAPI(title="Tetsuya Daemon", default_response_class=ORJSONUtcResponse)
