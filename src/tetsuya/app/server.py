"""Server implements logic for starting and verifying server."""

from __future__ import annotations

import os
import sys
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import logistro
import platformdirs
import uvicorn

from . import services
from ._server_globals import app

if TYPE_CHECKING:
    from .services._protocol import Bannin


_logger = logistro.getLogger(__name__)

# The folder where we'll create a socket
runtime = platformdirs.user_runtime_dir("tetsuya", "pikulgroup")


# A list of possible services
service_types: list[type[Bannin]] = [
    services.SearchGit,
]

# A list of running services
active_services: list[Bannin] = []


def uds_path() -> Path:
    """Return default socket path."""
    base = Path(runtime)
    p = base / "tetsuya.sock"
    p.parent.mkdir(parents=True, exist_ok=True)
    _logger.info(f"Socket path: {p!s}")
    return p


def is_server_alive(uds_path: Path) -> bool:
    """Check if server is running."""
    if not uds_path.exists():
        return False
    try:
        transport = httpx.HTTPTransport(uds=str(uds_path))
        with httpx.Client(
            timeout=httpx.Timeout(0.05),
            transport=transport,
            base_url="http://tetsuya",
        ) as client:
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


def start():
    """Start the server."""
    active_services.extend([f() for f in service_types])
    if not is_server_alive(p := uds_path()):
        for _s in active_services:
            _logger.info(f"Found: {_s.__class__.__name__}")
        os.umask(0o077)
        _logger.info("Starting server.")
        uvicorn.run(app, uds=p)
    else:
        print("Server already running.", file=sys.stderr)  # noqa: T201
        sys.exit(1)


@app.get("/ping")
def ping():
    """Ping!"""  #  noqa: D400
    _logger.info("Pong!")
    return "pong"
