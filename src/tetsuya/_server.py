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

from ._server_globals import app
from .search_git import SearchGit

if TYPE_CHECKING:
    from ._protocol import Bannin

_logger = logistro.getLogger(__name__)
_logger.setLevel("INFO")

# The folder where we'll create a socket
runtime = platformdirs.user_runtime_dir("tetsuya", "pikulgroup")


# A list of possible services
service_types: list[type[Bannin]] = [
    SearchGit,
]

# A list of running services
services: list[Bannin] = []


def uds_path() -> Path:
    base = Path(runtime)
    p = base / "tetsuya.sock"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def is_server_alive() -> bool:
    if not (p := uds_path()).exists():
        return False
    try:
        transport = httpx.HTTPTransport(uds=str(p))
        with httpx.Client(
            timeout=httpx.Timeout(0.05),
            transport=transport,
            base_url="http://tetsuya",
        ) as client:
            r = client.get("/ping")
            if r.status_code == HTTPStatus.OK:
                _logger.info("Socket ping returned OK.")
                return True
            else:
                _logger.info(f"Socket ping returned {r.status_code}.")
                uds_path().unlink()
                return False
    except httpx.TransportError:
        _logger.info("Transport error in socket.")
        uds_path().unlink()
        return False


def start():
    services.extend([f() for f in service_types])
    if not is_server_alive():
        os.umask(0o077)
        uvicorn.run(app, uds=uds_path())
    else:
        print("Server already running.", file=sys.stderr)  # noqa: T201
        sys.exit(1)


@app.get("/ping")
def ping():
    return {}
