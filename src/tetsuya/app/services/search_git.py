"""Exposes a SearchGit service to find git repos below your home."""

import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import logistro

from . import _protocol
from .utils.config import config_data

_logger = logistro.getLogger(__name__)

# These will have to be versioned
# And they will have to have migratory functions
# They should also be logged
# And their constructors should reasonably take an old version


@dataclass()
class SearchGitStorage:
    """Service to search operating system for git repos."""

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


class SearchGit(_protocol.Bannin):  # is Bannin
    """SearchGit is a class to find git repos below your home directory."""

    def __init__(self):
        """Construct a SearchGit service."""
        self.name = "SearchGit"
        self.cachelife = timedelta(hours=12)
        self.version = 0
        self.cache = None
        # check if reloading (cache)

    def _execute(self) -> SearchGitStorage:
        """Execute search of your home repository for git repos."""
        home = Path.home()

        _c = config_data.get(self.name, {})
        ignore_folders = _c.get("ignore_folders", [])
        _logger.info(f"Ignoring folders: {ignore_folders}")
        ignore_paths = _c.get("ignore_paths", [])
        _logger.info(f"Ignoring paths: {ignore_paths}")

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
        _logger.info(" ".join(cmd))
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
