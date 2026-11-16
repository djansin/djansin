from dataclasses import dataclass

from core.types.mixins import ToDictMixin


@dataclass(frozen=True, slots=True)
class Result(ToDictMixin):
    """Base class for all service/API result objects."""
