"""These globals, needed everywhere, cannot depend on anything."""

from __future__ import annotations

import logistro
import typer
from fastapi import FastAPI

_logger = logistro.getLogger(__name__)

cli = typer.Typer(help="tetsuya CLI")
# Our server daemon
app = FastAPI(title="Tetsuya")


def main():  # script entry point
    """Start the cli service."""
    _, remaining = logistro.parser.parse_known_args()
    cli(args=remaining)
