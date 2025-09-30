from datetime import timedelta
from typing import Protocol


class Bannin(Protocol):
    name: str
    cachelife: timedelta
    version: int

    def do(self) -> None: ...

    # add run
    # add dataclass?
    # add expression
