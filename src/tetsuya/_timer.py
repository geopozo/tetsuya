"""Periodically refreshes data, if need-be."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import TYPE_CHECKING, TypedDict

import logistro

from . import _config

if TYPE_CHECKING:
    from .services._base import Bannin, Han


class TaskData(TypedDict):
    """A task and its data."""

    task: asyncio.Task
    cachelife: int
    tstamp: datetime  # when task was created
    duration: int
    service: Bannin


timer_tasks: dict[str, TaskData] = {}

_logger = logistro.getLogger(__name__)


def _post_task(service_and_def: tuple[Bannin, Han], t: int = 0):
    service, han = service_and_def
    cfg = _config.get_active_config(han)
    if not cfg:
        raise RuntimeError(
            f"_timer can't find a configuration for service {han.service.get_name()}",
        )

    async def _delayed_task(service: Bannin, t: int):
        await asyncio.sleep(t)
        _logger.info(
            f"Timer fired for {service.get_name()} @ {datetime.now(tz=UTC)}",
        )
        await service.run(cfg)

    _t = asyncio.create_task(_delayed_task(service, t))

    timer_tasks[service.get_name()] = {
        "task": _t,
        "cachelife": cfg.cachelife,
        "tstamp": datetime.now(tz=UTC),
        "duration": t,
        "service": service,
    }

    def _clear_task(t: asyncio.Task):
        if t.cancelled():  # don't reschedule, assume descheduled
            return
        elif e := t.exception():
            _logger.error("Error while timer clears a task.", exc_info=e)
        reschedule(service_and_def)

    _t.add_done_callback(_clear_task)


def reschedule(service_and_def: tuple[Bannin, Han]):
    service, han = service_and_def
    cfg = _config.get_active_config(han)
    if not cfg:
        raise RuntimeError(
            f"_timer can't find a configuration for service {han.service.get_name()}",
        )
    deschedule(service)
    if not cfg.autorefresh:
        _logger.info(f"No need to reschedule {service.get_name()}, no autorefresh.")
        return

    if not (last_report := service.get_report()) or not last_report.is_live(cfg):
        for_when = 0
    else:
        for_when = max(
            0,
            (last_report.expiry(cfg) - datetime.now(tz=UTC)).total_seconds(),
        )

    _logger.info(f"Rescheduling task for {service.get_name()}")
    _post_task(service_and_def, t=int(for_when))


def deschedule(service: Bannin):
    if _td := timer_tasks.pop(service.get_name(), None):
        _td["task"].cancel()
