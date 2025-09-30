"""app providers the server and its services, as well as script entry."""

import logistro

from tetsuya._globals import cli

from . import server as server  # need this to be executed

_logger = logistro.getLogger(__name__)


def main():  # script entry point
    """Start the cli service."""
    _, remaining = logistro.parser.parse_known_args()
    cli(args=remaining)
