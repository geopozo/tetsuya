"""Bottom dependency."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import NamedTuple, TypeVar, cast

import logistro

_logger = logistro.getLogger(__name__)


@dataclass(slots=True)
class Settei:
    cachelife: int = 0  # number of seconds
    autorefresh: bool = False

    @classmethod
    def default_config(cls) -> Settei:
        return cls()


TSettei = TypeVar("TSettei", bound=Settei)


class Tsuho(ABC):
    """The object a service stores or returns."""

    @abstractmethod
    def long(self) -> str: ...

    @abstractmethod
    def short(self) -> str: ...

    created_at: datetime | None = None

    def _is_stamped(self) -> bool:  # make typeguard
        return bool(hasattr(self, "created_at") and self.created_at is not None)

    def time_since(self) -> timedelta | None:
        if not self._is_stamped() and self.created_at:  # typer
            return None
        if not isinstance(self.created_at, datetime):
            raise TypeError("Unreachable")
        return datetime.now(tz=UTC) - self.created_at

    def tstamp(self) -> None:
        self.created_at = datetime.now(tz=UTC)

    def expiry(self, config: Settei) -> datetime:
        if not self._is_stamped() or not hasattr(config, "cachelife"):
            return datetime.now(tz=UTC)
        else:
            if not isinstance(self.created_at, datetime):
                raise TypeError("Unreachable")
            return self.created_at + timedelta(seconds=config.cachelife)

    def is_live(self, config: Settei) -> bool:
        if not self._is_stamped() or self.created_at is None:
            return False
        return self.expiry(config) > datetime.now(tz=UTC)


class Bannin[TSettei](ABC):
    """The abstract idea of a service."""

    @classmethod
    def get_name(cls) -> str:
        """Get name of service."""
        return cls.__name__

    cache: Tsuho | None

    @abstractmethod
    def _execute(self, cfg: TSettei) -> Tsuho: ...

    def get_report(self) -> Tsuho | None:
        """Get the actual latest result object."""
        if not hasattr(self, "cache"):
            self.cache = None
        return self.cache

    async def run(self, cfg: TSettei, *, force=False):
        """Run the service in a cache-aware manner."""
        _logger.info(f"Running {self.get_name()}")

        cache = self.get_report()
        if (
            not force
            and hasattr(cache, "is_live")
            and cache
            and cache.is_live(config=cast("Settei", cfg))  # hate this
        ):
            _logger.info("Not rerunning- cache is live.")
            return
        cache = await asyncio.to_thread(self._execute, cfg)
        if hasattr(cache, "tstamp") and cache:
            cache.tstamp()
        self.cache = cache

        _logger.debug2(f"New cache: {self.cache}")


class Han(NamedTuple):
    config: type[Settei]
    report: type[Tsuho]
    service: type[Bannin]
