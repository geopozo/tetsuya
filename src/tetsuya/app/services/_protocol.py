"""Bottom dependency."""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Protocol

import logistro

_logger = logistro.getLogger(__name__)


class Output(Protocol):
    """The object a service stores or returns."""

    created_at: datetime

    def long(self) -> str: ...
    def short(self) -> str: ...


class Bannin(Protocol):
    """The abstract idea of a service."""

    name: str
    cachelife: timedelta
    version: int
    cache: Output | None

    @classmethod
    def default_config(cls) -> dict: ...
    def _execute(self) -> Output: ...

    def _is_expired(self):
        return not (
            self.cache
            and (self.cache.created_at + self.cachelife < datetime.now(tz=UTC))
        )

    def object(self):
        """Get the actual latest result object."""
        return self.cache

    async def run(self, *, force=False):
        """Run the service in a cache-aware manner."""
        if not force and not self._is_expired():
            _logger.info("Not rerunning- cache is alive.")
            return
        self.cache = await asyncio.to_thread(self._execute)
