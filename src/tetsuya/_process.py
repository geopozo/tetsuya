"""Server implements logic for starting and verifying server."""

from __future__ import annotations

import os
import sys
from http import HTTPStatus
from typing import TYPE_CHECKING

import httpx
import logistro
import uvicorn

from tetsuya.core import daemon

from .core.utils import get_http_client, uds_path

if TYPE_CHECKING:
    from pathlib import Path

_logger = logistro.getLogger(__name__)


def is_server_alive(uds_path: Path) -> bool:
    """Check if server is running."""
    if not uds_path.exists():
        return False
    client: None | httpx.Client = None
    try:
        client = get_http_client(uds_path, defer_close=False)
        r = client.get("/ping")
        if r.status_code == HTTPStatus.OK:
            _logger.info("Socket ping returned OK- server alive.")
            return True
        else:
            _logger.info(
                f"Socket ping returned {r.status_code}, removing socket.",
            )
            uds_path.unlink()
            return False
    except httpx.TransportError:
        _logger.info("Transport error in socket, removing socket.")
        uds_path.unlink()
        return False
    finally:
        if client:
            client.close()


async def start():
    if not is_server_alive(p := uds_path()):
        os.umask(0o077)
        _logger.info("Starting server.")
        server = uvicorn.Server(
            uvicorn.Config(
                daemon,
                uds=str(p),
                loop="asyncio",
                lifespan="on",
                reload=False,
            ),
        )

        await server.serve()  # calling the shortcut run would actually block the thread
    else:
        print("Server already running.", file=sys.stderr)  # noqa: T201
        sys.exit(1)
