from .search_git import SearchGit

register = [
    SearchGit(),
]

__all__ = [
    "register",
]
