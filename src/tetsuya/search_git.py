"""Exposes a SearchGit service to find git repos below your home."""

import subprocess
from pathlib import Path

import logistro

from ._config import config_data

_logger = logistro.getLogger(__name__)


class SearchGit:  # is Bannin
    """SearchGit is a class to find git repos below your home directory."""

    name: str
    time: int
    version: int
    config: dict  # not typed at the moment

    def __init__(self):
        """Construct a SearchGit service."""
        self.name = "SearchGit"
        self.time = 60 * 60 * 12
        self.version = 0
        self.load_config()
        # check if reloading (cache)

    # should verify config
    def load_config(self):  # needs to be type
        """Load config."""
        self.config = config_data.get(self.name, {})

    def do(self):
        """Execute search of your home repository for git repos."""
        home = Path.home()

        ignore_folders = self.config.get("ignore_folders", [])
        ignore_paths = self.config.get("ignore_paths", [])

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

        _repos = sorted({p for p in stdout.decode(errors="ignore").split("\n") if p})
        print(retval)  # noqa: T201
        print(stderr)  # noqa: T201
        print("\n".join(_repos))  # noqa: T201
