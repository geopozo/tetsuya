from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, TypedDict

import logistro

if TYPE_CHECKING:
    from .app.services._base import Bannin

class TaskData(TypedDict):
    task: asyncio.Task
    cachelife: int
    tstamp: datetime
    service: Bannin

timer_tasks: dict[str, TaskData] = {}

_logger = logistro.getLogger(__name__)

def reconfig(service: Bannin):
    cfg = service.get_config()
    if not cfg.autorefresh:
        deschedule(service)
    else:
        if not (_td := timer_tasks.get(service.get_name())):
            reschedule(service, for_when=0)
        else:
            if _td["cachelife"] != cfg.cachelife:
                duedate = _td["tstamp"] + timedelta(seconds=cfg.cachelife)
                if duedate <= datetime.now(tz=UTC):
                    reschedule(_td["service"], for_when=0)
                else:
                    for_when = (duedate - datetime.now(tz=UTC)).total_seconds()
                    reschedule(_td["service"], for_when=int(for_when))

def _clear_task(t: asyncio.Task):
    if t.cancelled():
        return
    else:
        if (e := t.exception()):
            _logger.error("Error while timer clears a task.", exc_info=e)

def _post_task(service: Bannin, t: int = 0):
    async def _delayed_task(service: Bannin, t: int):
        await asyncio.sleep(t)
        _logger.info(f"Timer fired for {service.get_name()} @ {datetime.now()}")
        await service.run()

    _t = asyncio.create_task(_delayed_task(service, t))
    timer_tasks[service.get_name()] = {
        "task": _t,
        "cachelife": service.get_config().cachelife,
        "tstamp": datetime.now(tz=UTC),
        "service": service,
        }
    _t.add_done_callback(_clear_task)


def reschedule(service: Bannin, *, for_when: int | None = None):
    _logger.info(f"Rescheduling {service.get_name()}")
    deschedule(service)
    _post_task(
        service,
        t = (
            for_when
            if for_when is not None
            else service.get_config().cachelife
            )
        )

def deschedule(service: Bannin):
    if _td := timer_tasks.pop(service.get_name(), None):
        _td["task"].cancel()

