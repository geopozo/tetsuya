import tomllib
from pathlib import Path

import logistro
import platformdirs

_logger = logistro.getLogger(__name__)

config_dir = Path(platformdirs.user_config_dir("tetsuya", "pikulgroup"))

if config_dir.is_file():
    with config_dir.open("rb") as f:
        config_data = tomllib.load(f)
else:
    _logger.info("No config file found.")
    config_data = {}


def touch():
    config_dir.touch()
    return str(config_dir.resolve())
