"""Tools for managing the global config."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

import logistro
import platformdirs
import tomli_w

if TYPE_CHECKING:
    from typing import Any

    from .services._base import Han, Settei

_logger = logistro.getLogger(__name__)

config_file = (
    Path(platformdirs.user_config_dir("tetsuya", "pikulgroup")) / "config.toml"
)

config_data: dict[Any, Any] = {}


def load_config() -> bool:
    if config_file.is_file():
        with config_file.open("rb") as f:
            config_data.clear()
            config_data.update(tomllib.load(f))
        return True
    else:
        _logger.info("No config file found.")
        return False


def get_active_config(service_def: Han) -> Settei | None:
    # could cache
    han = service_def
    _d = config_data.get(han.service.get_name())
    return han.config(**_d) if _d else None


def set_default_config(service_def: Han, *, overwrite: bool = False) -> bool:
    key = service_def.service.get_name()
    if key in config_data and not overwrite:
        return False
    config_data[key] = service_def.config.default_config()
    return True


def write_config():
    with config_file.open("wb") as f:
        tomli_w.dump(config_data, f)
