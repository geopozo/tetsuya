"""Tools for managing the global config."""

from __future__ import annotations

import asyncio
import tomllib
from http import HTTPStatus
from pathlib import Path

import logistro
import platformdirs
import tomli_w
import typer
from fastapi.responses import JSONResponse

from tetsuya._globals import app, cli, service_types
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


# this should maybe have print? overwrite doesn't really make sense
@config_cli.command()
def touch(*, default: bool = False, force: bool = False, dump: bool = False):
    """Create config file if it doesn't exist."""
    client = get_client()
    _logger.debug("Sending touch command.")
    r = client.put(
        "/config/touch",
        json={"default": default, "force": force},
    )
    _logger.debug("Processing touch response")
    # check return value
    if r.status_code == HTTPStatus.OK:
        result = r.json()
        if not dump:
            print(result.get("path", f"Weird result: {result}"))  # noqa: T201
        else:
            print(result.get("content", f"Weird result: {result}"))  # noqa: T201
    else:
        raise ValueError(f"{r.status_code}: {r.text}")


@app.put("/config/touch")
async def _touch(data: dict):
    """Create the config file if it doesn't exist."""
    _logger.info("Touching config file.")
    _logger.info(f"Touch received data: {data}")

    config_file.parent.mkdir(parents=True, exist_ok=True)

    if data.get("default"):
        config_dict = {}
        for t in service_types:
            if hasattr(t, "default_config"):
                d = config_dict.setdefault(t.__name__, {})
                d.update(t.default_config())
        if not config_file.exists() or data.get("force"):
            await asyncio.to_thread(config_file.write_text, tomli_w.dumps(config_dict))
        else:
            return JSONResponse(
                content={"error": "File exists. Use --force."},
                status_code=409,
            )
    else:
        config_file.touch()
    text = config_file.read_text(encoding="utf-8")
    ret = {"path": str(config_file.resolve()), "content": text}
    _logger.info(f"Touch sending back: {ret}")
    return ret
