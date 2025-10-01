"""services contains the services plus their utilities."""

from __future__ import annotations

import asyncio
from dataclasses import asdict, is_dataclass
from http import HTTPStatus
from typing import TYPE_CHECKING, Literal

import logistro
import typer
from fastapi.responses import JSONResponse

from tetsuya._globals import active_services, app, cli
from tetsuya.app.client import get_client

from . import utils as utils
from .search_git import SearchGit

if TYPE_CHECKING:
    from typing import Any

__all__ = ["SearchGit"]

_logger = logistro.getLogger(__name__)

service_cli = typer.Typer(help="Manage the services.")
cli.add_typer(service_cli, name="service")


@service_cli.command(name="list")  # accept --all
def _list():
    """List running services, or all services with --all."""
    client = get_client()
    _logger.info("Sending list command.")
    r = client.post(
        "/service/list",
    )
    # check return value
    if r.status_code == HTTPStatus.OK:
        for s in r.json():
            print(s)  # noqa: T201
    else:
        raise ValueError(f"{r.status_code}: {r.text}")


@app.post("/service/list")
async def __list():
    """List running services, or all services with --all."""
    return list(active_services.keys())


@service_cli.command(name="run")  # accept --all
def run(
    name: str | None = None,
    *,
    all: bool = False,  # noqa: A002
    force: bool = False,
    format: Literal["short", "long", "json"] = "json",  # noqa: A002
    # accept a cache controller here
):
    """Run a or all services."""
    client = get_client(timeout=10)
    _logger.info("Sending run command.")
    r = client.post(
        "/service/run",
        json={
            "name": name,
            "all": all,
            "force": force,
            "format": format,
        },
    )
    # check return value
    if r.status_code == HTTPStatus.OK:
        if format == "json":
            print(r.text)  # noqa: T201
        else:
            json = r.json()
            if len(json) == 1 and name in json:
                print(json[name])  # noqa: T201
            else:
                for k, v in json.items():
                    print(f"{k}:")  # noqa: T201
                    print(v)  # noqa: T201

    else:
        raise ValueError(f"{r.status_code}: {r.text}")


@app.post("/service/run")
async def _run(data: dict):  # noqa: C901, PLR0912
    """Run a or all services."""
    _n = data.get("name")
    _logger.info(f"Received service run request: {data}")
    if not _n and not data.get("all"):
        return JSONResponse(
            content={"error": "Supply either name or --all, not both."},
            status_code=400,
        )
    if _n and data.get("all"):
        return JSONResponse(
            content={"error": "Use either name or --all, not both."},
            status_code=400,
        )
    elif data.get("force") and data.get("cache"):
        return JSONResponse(
            content={"error": "Use either --force or --cache, not both."},
            status_code=400,
        )
    if _n and _n not in active_services:
        return JSONResponse(
            content={"error": f"Service {_n} not found."},
            status_code=404,
        )
    services = {_n: active_services[_n]} if _n else active_services
    tasks = {}
    k: Any
    v: Any
    for k, v in services.items():
        tasks[k] = asyncio.create_task(
            v.run(force=data.get("force", False)),
        )
    results = {}
    for k, v in tasks.items():
        await v
        _r = services[k].get_object()
        if _r is None:
            raise RuntimeError(f"Run failed for {k}")
        match data.get("format"):
            case "short":
                results[k] = _r.short()
            case "long":
                results[k] = _r.long()
            case "json":
                if not is_dataclass(_r):
                    raise RuntimeError(f"Cache for {k} is bad.")
                else:
                    results[k] = asdict(_r)
            case _:
                _logger.error(f"Unknown format: {data.get('format')}")
    _logger.debug2(f"Returning results: {results}")
    return results
