from typing import Protocol


class Bannin(Protocol):
    name: str
    time: int
    version: int

    def load_config(self) -> None: ...
    def do(self) -> None: ...
