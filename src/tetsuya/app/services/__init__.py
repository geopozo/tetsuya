"""services contains the services plus their utilities."""

from http import HTTPStatus

import logistro
import typer

from tetsuya._globals import active_services, app, cli
from tetsuya.app.client import get_client

from . import utils as utils
from .search_git import SearchGit

__all__ = ["SearchGit"]

_logger = logistro.getLogger(__name__)

service_cli = typer.Typer(help="Manage the services.")
cli.add_typer(service_cli, name="service")


@service_cli.command(name="list")  # accept --all
def _list():
    """Reload config file."""
    client = get_client()
    _logger.debug("Sending reload command.")
    r = client.post(
        "/service/list",
    )
    # check return value
    if r.status_code == HTTPStatus.OK:
        for s in r.json():
            print(s)  # noqa: T201
    else:
        raise ValueError(f"{r.status_code}: {r.text}")


@app.post("/service/list")
async def _list():
    """List running services, or all services with --all."""
    return list(active_services.keys())
