from .base import BaseAppException, ExceptionSeverity
from .common import (
    AppError,
    AuthError,
    BusinessError,
    DatabaseError,
    ExternalError,
    HttpError,
    SystemError,
    ValidationError,
)


__all__ = [
    "AppError",
    "AuthError",
    "BusinessError",
    "DatabaseError",
    "ExternalError",
    "HttpError",
    "SystemError",
    "ValidationError",
    "BaseAppException",
    "ExceptionSeverity",
]
