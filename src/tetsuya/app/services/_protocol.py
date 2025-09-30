from datetime import datetime, timedelta
from typing import Protocol


class Output(Protocol):
    created_at: datetime


class Bannin(Protocol):
    name: str
    cachelife: timedelta
    version: int

    def execute(self) -> Output: ...

    # add run
    # add dataclass?
    # add expression
