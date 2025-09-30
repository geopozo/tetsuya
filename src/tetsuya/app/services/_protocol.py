from datetime import datetime, timedelta
from typing import Protocol


class Output(Protocol):
    """The object a service stores or returns."""

    created_at: datetime


class Bannin(Protocol):
    """The abstract idea of a service."""

    name: str
    cachelife: timedelta
    version: int

    def execute(self) -> Output: ...

    # add run
    # add dataclass?
    # add expression
