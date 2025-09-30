from http import HTTPStatus
from pathlib import Path

import httpx
import platformdirs
from fastapi import FastAPI

import logistro

_logger = logistro.getLogger(__name__)
_logger.setLevel("INFO")

runtime = platformdirs.user_runtime_dir("tetsuya", "pikulgroup")

app = FastAPI(title="Tetsuya")


def uds_path() -> Path:
    base = Path(runtime)
    p = base / "tetsuya.sock"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def is_server_alive() -> bool:
    if not (p := uds_path()).exists():
        return False
    try:
        transport = httpx.HTTPTransport(uds=str(p))
        with httpx.Client(
            timeout=httpx.Timeout(0.05),
            transport=transport,
            base_url="http://tetsuya",
        ) as client:
            r = client.get("/ping")
            if r.status_code == HTTPStatus.OK:
                _logger.info("Socket ping returned OK.")
                return True
            else:
                _logger.info(f"Socket ping returned {r.status_code}.")
                uds_path().unlink()
                return False
    except httpx.TransportError:
        _logger.info("Transport error in socket.")
        uds_path().unlink()
        return False


@app.get("/ping")
def ping():
    return {}
