"""Provides a server and client app for checking in on user-space services."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .search_git import SearchGit

if TYPE_CHECKING:
    from ._protocol import Bannin

__all__ = [
    "register",
]

register: list[Bannin] = [
    SearchGit(),
]
