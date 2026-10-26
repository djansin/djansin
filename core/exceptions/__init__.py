from .base import BaseAppException, ExceptionSeverity
from .categories import (
    AppError,
    AuthError,
    BusinessError,
    DatabaseError,
    DomainError,
    ExternalError,
    HttpError,
    InputError,
    SystemError,
    ValidationError,
)


__all__ = [
    "AppError",
    "AuthError",
    "BusinessError",
    "DatabaseError",
    "DomainError",
    "ExternalError",
    "HttpError",
    "InputError",
    "SystemError",
    "ValidationError",
    "BaseAppException",
    "ExceptionSeverity",
]
