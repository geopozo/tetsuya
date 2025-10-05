"""Bottom dependency."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Generic, TypeVar

import logistro

from .utils.config import config_data

if TYPE_CHECKING:
    from typing import Any


_logger = logistro.getLogger(__name__)

@dataclass(slots=True)
class Settei(ABC):
    cachelife: int = 0 # number of seconds
    autorefresh: bool = False

    @classmethod
    def default_config(cls) -> dict[str, Any]:
        return asdict(cls())

TSettei = TypeVar("TSettei", bound=Settei)

class Tsuho(ABC):
    """The object a service stores or returns."""

    @abstractmethod
    def long(self) -> str: ...

    @abstractmethod
    def short(self) -> str: ...

    created_at: datetime | None = None

    def _is_stamped(self) -> bool:
        return bool(hasattr(self, "created_at") and self.created_at) is not None

    def since_when(self) -> timedelta | None:
        if not self._is_stamped() or self.created_at is None: # redundant but typechecker dumb
            return None
        return datetime.now(tz=UTC) - self.created_at

    def tstamp(self) -> None:
        self.create_at = datetime.now(tz=UTC)

    def is_live(self, config: Settei | None) -> bool:
        if not self._is_stamped() or self.created_at is None:
            return False
        if not config or not hasattr(config, "cachelife"):
            return False
        return self.created_at + timedelta(seconds=config.cachelife) > datetime.now(tz=UTC)

class Bannin(ABC, Generic[TSettei]):
    """The abstract idea of a service."""

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Get name of service."""

    @classmethod
    @abstractmethod
    def get_config_type(cls) -> type[TSettei]:
        """Get a config dataclass."""

    cache: Tsuho | None

    @abstractmethod
    def _execute(self) -> Tsuho: ...

    def get_report(self) -> Tsuho | None:
        """Get the actual latest result object."""
        if not hasattr(self, "cache"):
            self.cache = None
        return self.cache

    async def run(self, *, force=False):
        """Run the service in a cache-aware manner."""
        _logger.info(f"Running {self.get_name()}")
        cache = self.get_report()
        if (
                not force
                and hasattr(cache, "is_live") and cache
                and cache.is_live(config=self.get_config())
                ):
            _logger.info("Not rerunning- cache is live.")
            return
        cache = await asyncio.to_thread(self._execute)
        if hasattr(cache, "tstamp") and cache:
            cache.tstamp()
        self.cache = cache

        _logger.debug2(f"New cache: {self.cache}")

    @classmethod
    def get_config(cls) -> TSettei:
        return cls.get_config_type()(**config_data.get(cls.get_name(), {}))
