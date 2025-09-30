"""Tools for managing the global config."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

import logistro
import platformdirs

from tetsuya.app._server_globals import app

if TYPE_CHECKING:
    from fastapi import Request

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


@app.put("/config/touch")
async def touch(request: Request):
    """Create the config file if it doesn't exist."""
    _data = await request.json()  # (should we get defaults)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.touch()
    return str(config_file.resolve())
