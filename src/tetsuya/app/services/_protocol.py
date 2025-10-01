"""Bottom dependency."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Protocol

import logistro

_logger = logistro.getLogger(__name__)

# I'm not entirely sure about the timer
# And it doesn't actually cache and load
# And there is no way to change it.


class Output(Protocol):
    """The object a service stores or returns."""

    created_at: datetime

    def long(self) -> str: ...
    def short(self) -> str: ...


class Bannin(Protocol):
    """The abstract idea of a service."""

    report_type: type[Output]
    name: str
    cachelife: timedelta
    version: int
    cache: Output | None
    _pending_task: asyncio.Task | None = None

    @classmethod
    def default_config(cls) -> dict: ...
    def _execute(self) -> Output: ...

    def _is_cache_live(self):
        return self.cache is not None and (
            self.cache.created_at + self.cachelife > datetime.now(tz=UTC)
        )

    def get_object(self) -> Output:
        """Get the actual latest result object."""
        if not self.cache:
            raise RuntimeError(f"Cache for {self.name} wont populate.")
        return self.cache

    def _clear_task(self, p: asyncio.Task):
        if p.cancelled():
            return
        if e := p.exception():
            _logger.error(e)  # TODO(AJP): check about _logger and exceptions
            # search exc_info in everything
            # also, this won't restart

    async def _run_in_a_while(self, time: int):
        await asyncio.sleep(time)
        await self.run()

    async def run(self, *, force=False):
        """Run the service in a cache-aware manner."""
        if not force and self._is_cache_live():
            _logger.info("Not rerunning- cache is live.")
            return
        if _p := self._pending_task:
            _p.cancel()
            await asyncio.sleep(0)  # let it cancel
        self.cache = await asyncio.to_thread(self._execute)
        _logger.debug2(f"New cache: {self.cache}")
        self._pending_task = asyncio.create_task(
            self._run_in_a_while(int(self.cachelife.total_seconds())),
        )
        self._pending_task.add_done_callback(self._clear_task)
