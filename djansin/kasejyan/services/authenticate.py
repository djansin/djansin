"""Service layer for authenticating and registering users.

This module defines :class:`AuthenticateService`, the primary entry point
for the sign-in/sign-up flow. It resolves an incoming identifier (username,
email address, or phone number) to a user record, logging in existing
accounts and provisioning new ones when the supplied credentials prove
ownership of the identifier.
"""

import contextlib

from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _t

from core.exceptions import ValidationError
from core.exceptions.errors.business import DuplicateResource
from core.services import Service
from core.utils import (
    generate_unique_username,
    is_valid_email,
    is_valid_phone,
)
from djansin.kasejyan.exceptions import InvalidLoginIdentifier
from djansin.kasejyan.models import Email, Phone, User
from djansin.kasejyan.services.verify_contact import VerifyContactService
from djansin.kasejyan.types import RegisteredUser


class AuthenticateService(Service[RegisteredUser]):
    """Coordinates login and registration for all supported identifiers.

    Dispatches authentication based on the shape of the incoming
    ``identifier``: email addresses and phone numbers are handled through
    their associated :class:`~djansin.kasejyan.models.Email` /
    :class:`~djansin.kasejyan.models.Phone` contact records, while
    everything else is treated as a username. Contact-based flows may
    either authenticate an existing account (with a password or a
    verification code) or lazily provision a new user on first successful
    verification.
    """

    def execute(
        self, identifier: str, password: str | None = None, code: None = None
    ) -> RegisteredUser:
        """Authenticate an existing user or register a new one.

        Chooses the contact-based path when ``identifier`` is a valid email
        address or phone number, and the username-based path otherwise.

        Args:
            identifier (str): The login identifier supplied by the client.
                May be a username, email address, or phone number.
            password (str | None, optional): The user's password, when
                authenticating via credentials. Defaults to ``None``.
            code (None, optional): Reserved placeholder for a verification
                code argument. Defaults to ``None``.

        Returns:
            User: The authenticated or newly created user instance.
        """
        if password is not None and code is not None:
            raise ValidationError(InvalidLoginIdentifier())

        if is_valid_email(identifier) or is_valid_phone(identifier):
            user = self._login_or_register_by_contact(identifier, password, code)

        else:
            user = self._login_or_register_by_username(identifier, password)

        return RegisteredUser(
            pk=user.pk,
            uuid=user.uuid,
            username=user.username,
            email=user.email.address if hasattr(user, "email") else None,
            phone=user.phone.number if hasattr(user, "phone") else None,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            date_joined=user.date_joined,
        )

    def _login_or_register_by_username(self, username: str, password: str) -> User:
        """Authenticate or register a user identified by username.

        Looks up an active user by ``username`` and, if found, verifies the
        supplied password. If no such user exists, a new account is created
        with the given credentials.

        Args:
            username (str): The unique username to authenticate or register.
            password (str): The raw password to check against an existing
                account, or to assign to a newly created one.

        Returns:
            User: The authenticated existing user, or the newly created
            user instance.
        """
        if password is None:
            raise ValidationError(InvalidLoginIdentifier())

        try:
            user = User.objects.get_by_username(username=username)
            if user.check_password(raw_password=password):
                return user

            raise ValidationError(InvalidLoginIdentifier())

        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password=password)
            return user

    def _login_or_register_by_contact(
        self, identifier: str, password: str | None, code: str | None
    ) -> User:
        """Authenticate or register a user via an email or phone contact.

        Resolves the contact record matching ``identifier`` and then:
            * If the contact is already linked to a user, authenticates
              either by verification code or by password.
            * If the contact is not yet linked, validates the supplied
              verification code and provisions a new user, attaching the
              contact to it.

        Args:
            identifier (str): A valid email address or phone number.
            password (str | None): The password used when authenticating an
                existing linked account.
            code (str | None): The one-time verification code used when
                authenticating or provisioning a contact.

        Returns:
            User: The authenticated or newly provisioned user instance.

        Raises:
            ValidationError: If the contact does not exist, neither a code
                nor a password is provided, the provided code is invalid,
                or the provided password does not match.
            BusinessError: If a newly generated username collides at the
                database level while provisioning a user.
        """
        contact = None
        user = None

        if is_valid_email(identifier):
            with contextlib.suppress(Email.DoesNotExist):
                contact: Email = Email.objects.find_by_address(identifier)

        elif is_valid_phone(identifier):
            with contextlib.suppress(Phone.DoesNotExist):
                contact: Phone = Phone.objects.find_by_number(identifier)

        if contact is None:
            raise ValidationError(InvalidLoginIdentifier())

        if code is not None:
            try:
                vc_service = VerifyContactService()
                vc_service(identifier=identifier, code=code)

            except ValidationError as e:
                raise ValidationError(InvalidLoginIdentifier()) from e

        elif password is not None:
            if contact.user and contact.user.check_password(raw_password=password):
                return contact.user

            else:
                raise ValidationError(InvalidLoginIdentifier())

        if contact.user is None:
            try:
                user = User.objects.create_user(
                    username=generate_unique_username(), password=None
                )
                contact.user = user
                contact.save(update_fields=["user"])

            except IntegrityError as e:
                raise ValidationError(
                    DuplicateResource(resource=_t("User"), field_name=_t("username"))
                ) from e

        return contact.user
