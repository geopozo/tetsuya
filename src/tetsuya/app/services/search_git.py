"""Exposes a SearchGit service to find git repos below your home."""

import asyncio
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import logistro

from .utils.config import config_data

_logger = logistro.getLogger(__name__)


# Should be a protocol
@dataclass()
class SearchGitStorage:
    retval: int
    stderr: str
    repos: list[Path]
    created_at: datetime = field(
        default_factory=lambda: datetime.now(tz=UTC),
    )

    def long(self) -> str:
        """One full path per line."""
        return "\n".join(str(p.resolve()) for p in sorted(self.repos))

    def short(self) -> str:
        """Comma-separated last directory names."""
        return ", ".join(p.name for p in sorted(self.repos))


class SearchGit:  # is Bannin
    """SearchGit is a class to find git repos below your home directory."""

    name: str
    cachelife: timedelta
    version: int
    last: SearchGitStorage | None

    def __init__(self):
        """Construct a SearchGit service."""
        self.name = "SearchGit"
        self.cachelife = timedelta(hours=12)
        self.version = 0
        self.last = None
        # check if reloading (cache)

    def _is_expired(self):
        return not (
            self.last and (self.last.created_at + self.cachelife < datetime.now(tz=UTC))
        )

    def short(self):
        return self.last.short() if self.last else "No data"

    def long(self):
        return self.last.long() if self.last else "No data"

    def object(self):
        return self.last

    async def run(self, *, force=False):
        if not force and not self._is_expired():
            return
        self.last = await asyncio.to_thread(self.execute)

    def execute(self) -> SearchGitStorage:
        """Execute search of your home repository for git repos."""
        home = Path.home()

        _c = config_data.get(self.name, {})
        ignore_folders = _c.get("ignore_folders", [])
        ignore_paths = _c.get("ignore_paths", [])

        # Build the prune expression:
        # ( -path <abs> -o -path <abs> -o -name <nm> -o ... )
        expr = []
        for p in ignore_paths:
            expr += ["-path", str(p)]
            expr += ["-o"]
        for name in ignore_folders:
            expr += ["-name", str(name)]
            expr += ["-o"]
        # drop last -o, close group, then -prune -o
        expr = [r"\(", *expr[:-1], r"\)", "-prune", "-o"] if expr else []

        cmd = [
            "find",
            str(home),
            *expr,
            "-type",
            "d",
            "-name",
            ".git",
            "-printf",
            "%h\n",  # print the parent dir of .git
            "-prune",  # and don't descend into the .git dir itself
        ]

        p = subprocess.run(  # noqa: S603
            cmd,
            check=False,
            capture_output=True,
        )
        retval, stdout, stderr = p.returncode, p.stdout, p.stderr

        _repos = sorted(
            {Path(p) for p in stdout.decode(errors="ignore").split("\n") if p},
        )

        return SearchGitStorage(retval=retval, stderr=stderr.decode(), repos=_repos)
