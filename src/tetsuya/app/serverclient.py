"""Server implements logic for starting and verifying server."""

from __future__ import annotations

import asyncio
import os
import sys

import logistro
import uvicorn

from tetsuya._globals import active_services, app, cli, service_types
from tetsuya.timer import reconfig

from .utils import is_server_alive, uds_path

_logger = logistro.getLogger(__name__)


@cli.command(name="server")
def start_server():
    """Start the server."""

    async def _start():
        active_services.update(
            {f.__name__: f() for f in service_types},
        )
        if not is_server_alive(p := uds_path()):
            for _n, _s in active_services.items():
                _logger.info(f"Found: {_n}")
                reconfig(_s)
            os.umask(0o077)
            _logger.info("Starting server.")
            server = uvicorn.Server(
                uvicorn.Config(
                    app,
                    uds=str(p),
                    loop="asyncio",
                    lifespan="on",
                    reload=False,
                ),
            )
            await server.serve()
        else:
            print("Server already running.", file=sys.stderr)  # noqa: T201
            sys.exit(1)

    asyncio.run(_start())


def start_client():  # script entry point
    """Start the cli service."""
    _, remaining = logistro.parser.parse_known_args()
    cli(args=remaining)


@app.get("/ping")
def ping():
    """Ping!"""  #  noqa: D400
    _logger.info("Pong!")
    return "pong"
