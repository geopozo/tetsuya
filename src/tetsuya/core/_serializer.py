"""These globals, needed everywhere, cannot depend on any tetsuya thing."""

from __future__ import annotations

import orjson
from fastapi.responses import Response


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
