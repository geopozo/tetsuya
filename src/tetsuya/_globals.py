"""These globals, needed everywhere, cannot depend on any tetsuya thing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import logistro
import orjson
import typer
from fastapi import FastAPI
from fastapi.responses import Response

if TYPE_CHECKING:
    from .app.services._protocol import Bannin

_logger = logistro.getLogger(__name__)


class ORJSONUtcResponse(Response):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return orjson.dumps(
            content,
            option=(
                orjson.OPT_NAIVE_UTC  # treat naive datetimes as UTC
                | orjson.OPT_UTC_Z  # use "Z" instead of +00:00
                | orjson.OPT_SERIALIZE_DATACLASS
                | orjson.OPT_SERIALIZE_NUMPY
            ),
        )


cli = typer.Typer(help="tetsuya CLI")
# Our server daemon
app = FastAPI(title="Tetsuya", default_response_class=ORJSONUtcResponse)

# A list of possible services
service_types: list[type[Bannin]] = []

# A list of running services, only activated by start
active_services: dict[str, Bannin] = {}
