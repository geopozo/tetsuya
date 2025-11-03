"""Tools for caching/storing results."""

import platformdirs

cache_dir = platformdirs.user_cache_dir("tetsuya", "pikulgroup")

# we only need a cache right now for reloads
