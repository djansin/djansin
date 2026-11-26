"""Models package for the Aalnan application.

Aggregates model classes from submodules within this package so consumers
can import them directly from the package root (e.g.,
`from djansin.aalnan.models import MyModel`) instead of referencing their
defining submodules. Each model should live in its own submodule and be
re-exported here via `from .<module> import <ModelClass>`.

Example:
    To expose a `User` model defined in `models/user.py`, add::

        from .user import User

Attributes:
    __all__ (list[str]): Public model names exported by this package.
"""

__all__: list[str] = []

