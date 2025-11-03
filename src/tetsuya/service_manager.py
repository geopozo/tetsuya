"""Tracks what services are available and what are running."""

### Big File Warning:
### It's the whole CLI/Daemon API. Fold it.
###

from __future__ import annotations

import asyncio
from dataclasses import asdict, is_dataclass
from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING, Literal

import logistro
import typer
from fastapi.responses import JSONResponse

from . import _config, _process, _timer, services
from .core import cli, daemon, utils
from .services._base import Han

if TYPE_CHECKING:
    from typing import Any

    from .services._base import Bannin

_logger = logistro.getLogger(__name__)

# A list of running services, only activated by start
active_services: dict[str, tuple[Bannin, Han]] = {}

server_cli = typer.Typer()
config_cli = typer.Typer()
server_cli.add_typer(config_cli, name="config")
cli.add_typer(server_cli, name="server")


def start_client():  # script entry point
    """Start the cli service."""
    logistro.betterConfig()
    _, remaining = logistro.parser.parse_known_args()
    cli(args=remaining)


@server_cli.command()
def start():
    """Start the tetsuya server."""

    async def foo():
        _config.load_config()
        for service_name in getattr(services, "__all__", []):
            service_def = getattr(services, service_name, None)
            if not service_def or not isinstance(service_def, Han):
                continue
            _logger.info(f"Loading {service_name}")

            if not _config.get_active_config(service_def):
                continue
            _s = active_services[service_name] = (service_def.service(), service_def)
            _timer.reschedule(_s)
        await _process.start()

    asyncio.run(foo())


@daemon.get("/ping")
def ping():
    """Ping!"""  #  noqa: D400
    _logger.info("Pong!")
    return "pong"


@daemon.post("/config/reload")
async def _reload():
    """Reload config file."""
    _logger.info("Reloading config file.")
    res = _config.load_config()
    if not res:
        return JSONResponse(
            content={},
            status_code=404,
        )
    for _service, _def in active_services.values():
        _logger.info(f"Resetting time for {_def.service.get_name()}")
        _timer.reschedule((_service, _def))
    return None


@config_cli.command()
def reload():
    """Reload config file."""
    client = utils.get_http_client()
    _logger.info("Sending reload command.")
    r = client.post(
        "/config/reload",
    )
    # check return value
    if r.status_code == HTTPStatus.OK:
        print("OK")  # noqa: T201
    else:
        raise ValueError(f"{r.status_code}: {r.text}")


@daemon.put("/config/touch")
async def _touch(data: dict):
    """Create the config file if it doesn't exist."""
    _logger.info("Touching config file.")
    _logger.info(f"Touch received data: {data}")

    _config.config_file.parent.mkdir(parents=True, exist_ok=True)

    if data.get("default"):
        for service_and_def in active_services.values():
            _, han = service_and_def
            _config.set_default_config(han)
            _timer.reschedule(service_and_def)
        await asyncio.to_thread(_config.write_config)
    else:
        _config.config_file.touch()

    text = _config.config_file.read_text(encoding="utf-8")
    ret = {"path": str(_config.config_file.resolve()), "content": text}
    _logger.info(f"Touch sending back: {ret}")
    return ret


@config_cli.command()  # foorcing doesn't do anything at the moment.
def touch(*, default: bool = False, force: bool = False, dump: bool = False):
    """Create config file if it doesn't exist."""
    client = utils.get_http_client()
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


service_cli = typer.Typer(help="Manage the services.")
cli.add_typer(service_cli, name="service")


@daemon.post("/service/list")
async def __list():
    """List running services, or all services with --all."""
    # last run, # next run, look in timer
    ret = []
    # this _name is lowercase because of how we load up services,
    # it should be changed. Use classname.
    for _name, _pair in active_services.items():
        _service, _def = _pair
        _timertask = _timer.timer_tasks.get(_service.get_name())
        tformat = "%a %b %e %I:%M:%S %p %z %Y"

        _rep = _timertask["service"].get_report() if _timertask else None
        last_run = (
            _rep.created_at.astimezone().strftime(tformat)
            if _rep and _rep.created_at
            else "Never"
        )
        next_run = (
            (_timertask["tstamp"] + timedelta(seconds=_timertask["duration"]))
            .astimezone()
            .strftime(tformat)
            if _timertask
            else "None"
        )
        ret.append(
            f"{_name}: Last Run: {last_run}; Next Run: {next_run};",
        )
    return ret


@service_cli.command(name="list")  # accept --all
def _list():
    """List running services, or all services with --all."""
    client = utils.get_http_client()
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


@daemon.post("/service/run")
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
        _logger.info(f"Creating {k!s} run task.")
        tasks[k] = asyncio.create_task(
            v[0].run(
                _config.get_active_config(v[1]),
                force=data.get("force", False),
            ),  # service as name
        )
    results = {}
    for k, v in tasks.items():
        await v
        _r = services[k][0].get_report()
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


@service_cli.command(name="run")  # accept --all
def run(
    name: str | None = None,
    *,
    all: bool = False,  # noqa: A002
    force: bool = False,
    format: Literal["short", "long", "json"] = "json",  # noqa: A002
    timeout: int = 10,
    # accept a cache controller here
):
    """Run a or all services."""
    client = utils.get_http_client(timeout=timeout)
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
