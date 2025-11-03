"""Utitilies for everyone. No deps."""

import atexit
from pathlib import Path

import httpx
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


def get_http_client(
    path: Path | None = None,
    *,
    defer_close=True,
    timeout=0.05,
) -> httpx.Client:
    """Get HTTP client."""
    p = path or uds_path()
    if not p.exists():
        raise RuntimeError("Server must be running.")
    """Get a client you can use for executing commands."""
    transport = httpx.HTTPTransport(uds=str(p))
    client = httpx.Client(
        timeout=httpx.Timeout(timeout),
        transport=transport,
        base_url="http://tetsuya",
    )
    if defer_close:
        atexit.register(client.close)
    return client
