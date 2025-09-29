from typing import Protocol


class Bannin(Protocol):
    name: str
    time: int
    version: int

    def do(self) -> None: ...
