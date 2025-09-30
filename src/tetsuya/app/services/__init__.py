"""Services containst the services plus their utilities."""

from tetsuya._globals import cli

from . import utils as utils
from .search_git import SearchGit

__all__ = ["SearchGit"]


@cli.command(name="service")
def _service(name: str):
    # from here, we make a client call to the server
    # are capacity to do that is in _server
    # its a matching endpoint
    pass
