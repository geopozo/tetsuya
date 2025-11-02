"""Utitilies for everyone. No deps."""

import atexit
from http import HTTPStatus
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


def is_server_alive(uds_path: Path) -> bool:
    """Check if server is running."""
    if not uds_path.exists():
        return False
    client: None | httpx.Client = None
    try:
        client = get_client(uds_path, defer_close=False)
        r = client.get("/ping")
        if r.status_code == HTTPStatus.OK:
            _logger.info("Socket ping returned OK- server alive.")
            return True
        else:
            _logger.info(
                f"Socket ping returned {r.status_code}, removing socket.",
            )
            uds_path.unlink()
            return False
    except httpx.TransportError:
        _logger.info("Transport error in socket, removing socket.")
        uds_path.unlink()
        return False
    finally:
        if client:
            client.close()


def get_client(
    path: Path | None = None,
    *,
    defer_close=True,
    timeout=0.05,
) -> httpx.Client:
    """Get a client you can use for executing commands."""
    transport = httpx.HTTPTransport(uds=str(path or uds_path()))
    client = httpx.Client(
        timeout=httpx.Timeout(timeout),
        transport=transport,
        base_url="http://tetsuya",
    )
    if defer_close:
        atexit.register(client.close)
    return client
