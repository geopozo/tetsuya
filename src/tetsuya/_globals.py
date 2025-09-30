"""These globals, needed everywhere, cannot depend on any tetsuya thing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import logistro
import typer
from fastapi import FastAPI

if TYPE_CHECKING:
    from .app.services._protocol import Bannin

_logger = logistro.getLogger(__name__)

cli = typer.Typer(help="tetsuya CLI")
# Our server daemon
app = FastAPI(title="Tetsuya")

# A list of possible services
service_types: list[type[Bannin]] = []
