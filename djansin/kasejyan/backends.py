"""Custom Django authentication backend supporting multiple identifier types.

This module provides :class:`UniversalAuthBackend`, a Django authentication
backend that lets users sign in with any of the identifiers supported by the
application: a username, an email address, or a phone number. The backend
normalizes the raw identifier, dispatches to the appropriate manager lookup,
and enforces Django's standard ``is_active`` check before returning the user.
"""

import contextlib

from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest

from core.utils.user_identifier import is_valid_email, is_valid_phone
from djansin.kasejyan.models import User


class UniversalAuthBackend(ModelBackend):
    """Authentication backend accepting username, email, or phone identifiers.

    Extends :class:`~django.contrib.auth.backends.ModelBackend` to allow a
    single ``identifier`` argument to resolve to a user through any of the
    application's supported identifier types. The backend:

    * Trims surrounding whitespace from the identifier.
    * Treats syntactically valid email addresses and phone numbers as
      contact-based identifiers, delegating lookup to the related
      :class:`~djansin.kasejyan.models.Email` or
      :class:`~djansin.kasejyan.models.Phone` manager.
    * Treats any other value as a username lookup.
    * Runs Django's standard ``user_can_authenticate`` check so inactive
      accounts are rejected.
    * Returns ``None`` for any unknown identifier or invalid password, as
      required by the Django authentication contract.

    Example:
        A user may authenticate using any of the following identifiers::

            "john_doe"               # username
            "john@example.com"       # email address
            "+989123456789"          # phone number
    """

    def authenticate(
        self,
        request: HttpRequest,
        identifier: str | None = None,
        password: str | None = None,
        **kwargs,
    ) -> User | None:
        """Authenticate a user by username, email address, or phone number.

        Resolves the user identified by ``identifier`` using the appropriate
        lookup strategy and validates the supplied ``password``. The method
        never raises for unknown or malformed identifiers; it returns
        ``None`` in every failure case to comply with Django's backend
        contract.

        Args:
            request (HttpRequest): The current HTTP request. Passed through
                to Django's permission hooks; unused by this backend.
            identifier (str | None): The authentication identifier. May be a
                username, email address, or phone number. Defaults to
                ``None``.
            password (str | None): The plaintext password to validate.
                Defaults to ``None``.
            **kwargs: Additional keyword arguments forwarded by Django's
                authentication machinery (e.g. ``username`` when called
                positionally from ``authenticate()``).

        Returns:
            User | None: The authenticated user when the identifier resolves
            and the password matches, otherwise ``None``.
        """
        # Django may call this backend with ``username=`` as a keyword
        # argument (e.g. via ``django.contrib.auth.authenticate``), so fall
        # back to ``kwargs`` when the explicit ``identifier`` is absent.
        if identifier is None:
            identifier = kwargs.get("username")

        if identifier is None or password is None:
            return None

        user = self._resolve_user(identifier=identifier)

        if user is None:
            return None

        if not self.user_can_authenticate(user):
            return None

        if user.check_password(raw_password=password):
            return user

        return None

    def _resolve_user(self, identifier: str) -> User | None:
        """Resolve a raw identifier to a user, or ``None`` if not found.

        Normalizes the supplied identifier and dispatches to the correct
        manager lookup. Contact-based lookups suppress ``DoesNotExist`` so
        the caller always receives ``None`` on miss.

        Args:
            identifier (str): The raw identifier supplied by the client.
                May be a username, email address, or phone number, or a
                value whose ``str`` representation is one of those.

        Returns:
            User | None: The matching active user, or ``None`` when no user
            matches the identifier.
        """
        # Normalize: allow ``PhoneNumber`` (and similar) instances to be
        # passed through safely, and strip incidental whitespace.
        identifier = str(identifier).strip()

        if is_valid_email(identifier=identifier):
            with contextlib.suppress(User.DoesNotExist):
                return User.objects.get_by_email(address=identifier)

        elif is_valid_phone(identifier=identifier):
            with contextlib.suppress(User.DoesNotExist):
                return User.objects.get_by_phone(number=identifier)

        else:
            with contextlib.suppress(User.DoesNotExist):
                return User.objects.get_by_username(username=identifier)

        return None
