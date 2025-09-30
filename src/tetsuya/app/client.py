"""Contains helper functions for the client. Only utils dep."""

import atexit
from pathlib import Path

import httpx

from .utils import uds_path


def get_client(path: Path | None, *, defer_close=True) -> httpx.Client:
    """Get a client you can use for executing commands."""
    transport = httpx.HTTPTransport(uds=str(path or uds_path()))
    client = httpx.Client(
        timeout=httpx.Timeout(0.05),
        transport=transport,
        base_url="http://tetsuya",
    )
    if defer_close:
        atexit.register(client.close)
    return client
