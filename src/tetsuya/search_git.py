import subprocess
from pathlib import Path

from ._config import config_data

import logistro

_logger = logistro.getLogger(__name__)


class SearchGit:  # is Bannin
    name: str
    time: int
    version: int

    def __init__(self):
        self.name = "SearchGit"
        self.time = 60 * 60 * 12
        self.version = 0
        self.load_config()
        # check if reloading (cache)

    # TODO: verify config
    def load_config(self):  # needs to be type
        """Load config."""
        self.config = config_data.get(self.name, {})

    def do(self):
        home = Path.home()

        ignore_folders = self.config.get("ignore_folders", [])
        ignore_paths = self.config.get("ignore_paths", [])

        # Build the prune expression: ( -path <abs> -o -path <abs> -o -name <nm> -o ... )
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
            "%h\n",  # print the parent dir of .git, NUL-separated
            "-prune",  # and don't descend into the .git dir itself
        ]

        p = subprocess.run(  # noqa: S603
            cmd,
            check=False,
            capture_output=True,
        )
        retval, stdout, stderr = p.returncode, p.stdout, p.stderr

        _repos = sorted({p for p in stdout.decode(errors="ignore").split("\n") if p})
        print(retval)
        print(stderr)
        print("\n".join(_repos))


# then, make a capn proto w/ socket
# create a proper return object for publishing and store it
# probably pickle object in cache
# create short, long, structures for publishing that return object
# it needs to be able to modify its config


# create help blurb
# create dependencies list "system"

# create some kind of timing thing

# add a statusbar hook

# add a line-be-line processor?

# Check for dirtiness or unpushed (based on this)
# Check for updates to linux
# Check for news
# Check for linux news
# Check for hackernews
