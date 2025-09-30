"""Utitilies for everyone. No deps."""

from pathlib import Path

import logistro
import platformdirs

_logger = logistro.getLogger(__name__)

# The folder where we'll create a socket
runtime_dir = platformdirs.user_runtime_dir("tetsuya", "pikulgroup")


def uds_path() -> Path:
    """Return default socket path."""
    base = Path(runtime_dir)
    p = base / "tetsuya.sock"
    p.parent.mkdir(parents=True, exist_ok=True)
    _logger.info(f"Socket path: {p!s}")
    return p
