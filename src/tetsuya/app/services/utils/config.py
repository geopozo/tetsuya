"""Tools for managing the global config."""

from __future__ import annotations

import tomllib
from http import HTTPStatus
from pathlib import Path

import logistro
import platformdirs
import typer

from tetsuya._globals import app, cli
from tetsuya.app.client import get_client

_logger = logistro.getLogger(__name__)

config_file = (
    Path(platformdirs.user_config_dir("tetsuya", "pikulgroup")) / "config.toml"
)

# need a reload
if config_file.is_file():
    with config_file.open("rb") as f:
        config_data = tomllib.load(f)
else:
    _logger.info("No config file found.")
    config_data = {}

config_cli = typer.Typer(help="Commands for managing the config.")
cli.add_typer(config_cli, name="config")


@config_cli.command()
def touch(*, default: bool = False, overwrite: bool = False):
    """Create config file if it doesn't exist."""
    client = get_client()
    _logger.debug("Sending touch command.")
    r = client.put(
        "/config/touch",
        json={"default": default, "overwrite": overwrite},
    )
    _logger.debug("Processing touch response")
    # check return value
    if r.status_code == HTTPStatus.OK:
        result = r.json()
        print(result.get("path", f"Weird result: {result}"))  # noqa: T201
    else:
        raise ValueError(f"{r.status_code}: {r.text}")


@app.put("/config/touch")
async def _touch(data: dict):
    """Create the config file if it doesn't exist."""
    _logger.info("Touching config file.")
    _logger.info(f"Touch received data: {data}")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.touch()
    ret = {"path": str(config_file.resolve())}
    _logger.info(f"Touch sending back: {ret}")
    return ret
