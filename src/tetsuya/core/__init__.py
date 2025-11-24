"""core provides the globals that every interface needs."""

import typer
from fastapi import FastAPI

from ._serializer import ORJSONUtcResponse

cli = typer.Typer(name="Tetsuya CLI")

daemon = FastAPI(title="Tetsuya Daemon", default_response_class=ORJSONUtcResponse)
