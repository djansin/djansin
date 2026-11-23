"""Base class for service-layer components.

This module defines :class:`Service`, a typed base class intended to be
inherited by concrete service classes across the project. It provides:

* a shared marker type for service-layer components,
* a generic ``execute`` contract with full type-hint support,
* centralized transaction management and error normalization.

Subclasses only need to implement :meth:`execute`; calling the service
instance directly (``service(...)``) triggers the managed pipeline.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, ClassVar, Generic, TypeVar, final

from django.db import transaction

from core.exceptions import SystemError
from core.exceptions.base import BaseAppException
from core.exceptions.errors.system import ServiceExecutionFailed


TResult = TypeVar("TResult")

TContext = Mapping[str, Any]


class Service(ABC, Generic[TResult]):
    atomic: ClassVar[bool] = False

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> TResult: ...

    @final
    def __call__(self, *args: Any, **kwargs: Any) -> TResult:
        try:
            if self.atomic:
                with transaction.atomic():
                    return self.execute(*args, **kwargs)
            return self.execute(*args, **kwargs)
        except BaseAppException:
            raise
        except Exception as exc:
            raise SystemError(ServiceExecutionFailed(reference_id="N/A")) from exc
