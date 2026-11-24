"""Universal authentication backend for identifier-based login.

Accepts an email address, phone number, or username as the ``identifier``
and authenticates the matching user against the supplied password.
Delegates the ``is_active`` check to
:meth:`~django.contrib.auth.backends.ModelBackend.user_can_authenticate`.

The backend does not consult verification codes; code-based sign-in is
handled by :class:`~djansin.kasejyan.services.authenticate.AuthenticateService`,
not by this backend.
"""

import contextlib

from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest

from core.utils.user_identifier import is_valid_email, is_valid_phone
from djansin.kasejyan.models import User


class UniversalAuthBackend(ModelBackend):
    """Authenticate a user by email, phone number, or username.

    Resolves the identifier to a user record, verifies the password,
    and delegates the ``is_active`` check to the base backend. Returns
    ``None`` on any failure (unknown identifier, wrong password,
    inactive user) so Django can try the next backend.
    """

    def authenticate(
        self,
        request: HttpRequest | None = None,
        identifier: str | None = None,
        password: str | None = None,
        **kwargs,
    ) -> User | None:
        """Authenticate a user by ``identifier`` and ``password``.

        Args:
            request (HttpRequest | None): The current request, or
                ``None`` when ``authenticate()`` is called outside a
                request cycle (e.g. from a management command).
            identifier (str | None): The email address, phone number,
                or username supplied by the client. When ``None``, the
                ``username`` keyword argument is used instead, for
                compatibility with Django's stock ``authenticate()``.
            password (str | None): The raw password to verify.
            **kwargs: Additional keyword arguments forwarded by
                Django's authentication machinery.

        Returns:
            User | None: The authenticated user, or ``None`` if the
            identifier is unknown, the password is wrong, or the user
            is inactive.
        """
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
        """Resolve ``identifier`` to a user record.

        Tries email, then phone number, then username. Returns ``None``
        if no user matches.

        Args:
            identifier (str): The email address, phone number, or
                username to resolve.

        Returns:
            User | None: The matching user, or ``None``.
        """
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
