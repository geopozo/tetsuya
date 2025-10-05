"""Exposes a SearchGit service to find git repos below your home."""

import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import logistro

from tetsuya._globals import service_types

from . import _base

_logger = logistro.getLogger(__name__)

@dataclass(slots=True)
class Config(_base.Settei):
    cachelife: int = 12 * 60 * 60
    autorefresh: bool = True
    ignore_folders: list[str] = field(default_factory=lambda: [".cache"])
    ignore_paths: list[str] = field(default_factory=list)

@dataclass()
class Report(_base.Tsuho):
    """Report format for SearchGit."""

    retval: int
    stderr: str
    repos: list[Path]

    def long(self) -> str:
        """One full path per line."""
        return "\n".join(str(p.resolve()) for p in sorted(self.repos))

    def short(self) -> str:
        """Comma-separated last directory names."""
        return ", ".join(p.name for p in sorted(self.repos))


class SearchGit(_base.Bannin[Config]):  # is Bannin
    """SearchGit is a class to find git repos below your home directory."""

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def get_config_type(cls):
        return Config

    def __init__(self):
        """Construct a SearchGit service."""

    def _execute(self) -> Report:
        """Execute search of your home repository for git repos."""
        home = Path.home()


        _cfg = self.get_config()
        _logger.info(f"Ignoring folders: {_cfg.ignore_folders}")
        _logger.info(f"Ignoring paths: {_cfg.ignore_paths}")

        # Build the prune expression:
        # ( -path <abs> -o -path <abs> -o -name <nm> -o ... )
        expr = []
        for p in _cfg.ignore_paths:
            expr += ["-path", str(p)]
            expr += ["-o"]
        for name in _cfg.ignore_folders:
            expr += ["-name", str(name)]
            expr += ["-o"]
        # drop last -o, close group, then -prune -o
        expr = [r"(", *expr[:-1], r")", "-prune", "-o"] if expr else []

        cmd = [
            "find",
            str(home),
            *expr,
            "-type",
            "d",
            "-name",
            ".git",
            "-printf",
            r"%h\n",  # print the parent dir of .git
            "-prune",  # and don't descend into the .git dir itself
        ]
        _logger.info(" ".join(cmd))
        p = subprocess.run(  # noqa: S603
            cmd,
            check=False,
            capture_output=True,
        )
        retval, stdout, stderr = p.returncode, p.stdout, p.stderr
        _logger.info("SearchGit ran command `find`.")
        _repos = sorted(
            {Path(p) for p in stdout.decode(errors="ignore").split("\n") if p},
        )
        # we are not skipping things properly
        rep = Report(retval=retval, stderr=stderr.decode(), repos=_repos)
        return rep


service_types.append(SearchGit)
