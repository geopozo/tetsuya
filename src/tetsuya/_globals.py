"""These globals, needed everywhere, cannot depend on any tetsuya thing."""

from __future__ import annotations

import logistro
import typer
from fastapi import FastAPI

_logger = logistro.getLogger(__name__)

cli = typer.Typer(help="tetsuya CLI")
# Our server daemon
app = FastAPI(title="Tetsuya")
