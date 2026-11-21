"""Service layer for authenticating and registering users.

Exposes :class:`AuthenticateService`, the primary entry point for the
sign-in/sign-up flow. It resolves an incoming identifier (username,
email address, or phone number) to a user record, logging in existing
accounts and provisioning new ones when the supplied credentials prove
ownership of the identifier.

Contact-based authentication via verification code is delegated to
:class:`~djansin.kasejyan.services.verify_contact.VerifyContactService`
with ``purpose=CodePurpose.AUTHENTICATE``, so a code issued for any
other operation (e.g. email change or password reset) is rejected.
Blocked contacts are also rejected by that service, so a temporarily
blocked email or phone cannot be used to sign in until the block
expires.
"""

from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _t

from core.exceptions import BusinessError, DomainError, ValidationError
from core.exceptions.errors.business import DuplicateResource
from core.exceptions.errors.validation import InvalidFormat
from core.services import Service
from core.utils import (
    generate_unique_username,
    is_valid_email,
    is_valid_phone,
)
from core.utils.user_identifier import is_valid_username
from djansin.kasejyan.exceptions import InvalidLoginIdentifier
from djansin.kasejyan.models import Email, Phone, User
from djansin.kasejyan.services.verify_contact import VerifyContactService
from djansin.kasejyan.types import RegisteredUser


class AuthenticateService(Service[RegisteredUser]):
    """Coordinates login and registration for all supported identifiers.

    Dispatches authentication based on the shape of the incoming
    ``identifier``: email addresses and phone numbers are handled
    through their associated :class:`~djansin.kasejyan.models.Email` /
    :class:`~djansin.kasejyan.models.Phone` contact records, while
    usernames are handled directly. Anything else is rejected with a
    validation error.

    Contact-based flows may either authenticate an existing account
    (with a password or a verification code) or lazily provision a new
    user on first successful verification. Verification codes are
    validated with ``purpose=CodePurpose.AUTHENTICATE``, so a code
    issued for a different operation (e.g. email change) is rejected.
    Blocked contacts are rejected by
    :class:`~djansin.kasejyan.services.verify_contact.VerifyContactService`
    before any code check.
    """

    def execute(
        self,
        identifier: str,
        password: str | None = None,
        code: str | None = None,
    ) -> RegisteredUser:
        """Authenticate an existing user or register a new one.

        Chooses the contact-based path when ``identifier`` is a valid
        email address or phone number, the username-based path when it
        is a valid username, and rejects anything else.

        Args:
            identifier (str): The login identifier supplied by the
                client. May be a username, email address, or phone
                number.
            password (str | None, optional): The user's password, when
                authenticating via credentials. Defaults to ``None``.
            code (str | None, optional): The one-time verification code,
                when authenticating via contact. Defaults to ``None``.

        Returns:
            RegisteredUser: The authenticated or newly created user,
            wrapped in a value object suitable for token issuance.

        Raises:
            DomainError: If both ``password`` and ``code`` are supplied,
                or if authentication fails for any reason.
            ValidationError: If ``identifier`` is not a valid email
                address, phone number, or username.
            BusinessError: If a newly generated username collides at the
                database level while provisioning a user.
        """
        if password is not None and code is not None:
            raise DomainError(InvalidLoginIdentifier())

        if is_valid_email(identifier) or is_valid_phone(identifier):
            user = self._login_or_register_by_contact(identifier, password, code)
        elif is_valid_username(identifier):
            user = self._login_or_register_by_username(identifier, password)
        else:
            raise ValidationError(
                InvalidFormat(
                    expected_format=_t(
                        "a valid email address, phone number, or username"
                    )
                )
            )

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

        Looks up a user by ``username`` and, if found, verifies the
        supplied password. If no such user exists, a new account is
        created with the given credentials.

        Args:
            username (str): The unique username to authenticate or
                register.
            password (str): The raw password to check against an
                existing account, or to assign to a newly created one.

        Returns:
            User: The authenticated existing user, or the newly created
            user instance.

        Raises:
            DomainError: If ``password`` is ``None`` or does not match
                the existing account.
        """
        if password is None:
            raise DomainError(InvalidFormat(expected_format=_t("a valid password")))

        try:
            user = User.objects.get_by_username(username=username)
            if user.check_password(raw_password=password):
                return user

            raise DomainError(InvalidLoginIdentifier())

        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password=password)
            return user

    def _login_or_register_by_contact(
        self,
        identifier: str,
        password: str | None,
        code: str | None,
    ) -> User:
        """Authenticate or register a user via an email or phone contact.

        Resolves the contact record matching ``identifier`` and then:

        * If the contact is already linked to a user, authenticates
          either by verification code or by password.
        * If the contact is not yet linked, validates the supplied
          verification code and provisions a new user, attaching the
          contact to it.

        Verification codes are validated with
        ``purpose=CodePurpose.AUTHENTICATE``; blocked contacts are
        rejected by the verification service before the code is checked.

        Args:
            identifier (str): A valid email address or phone number.
            password (str | None): The password used when authenticating
                an existing linked account.
            code (str | None): The one-time verification code used when
                authenticating or provisioning a contact.

        Returns:
            User: The authenticated or newly provisioned user instance.

        Raises:
            DomainError: If the contact does not exist, is temporarily
                blocked, neither a code nor a password is provided, the
                provided code is invalid or issued for a different
                purpose, or the provided password does not match.
            BusinessError: If a newly generated username collides at
                the database level while provisioning a user.
        """
        contact = None
        user = None

        if is_valid_email(identifier):
            contact = Email.objects.find_by_address(address=identifier)
        elif is_valid_phone(identifier):
            contact = Phone.objects.find_by_number(number=identifier)

        if contact is None:
            raise DomainError(InvalidLoginIdentifier())

        if code is not None:
            try:
                VerifyContactService()(
                    identifier=identifier,
                    code=code,
                    purpose=contact.CodePurpose.AUTHENTICATE,
                )
            except DomainError as e:
                raise DomainError(InvalidLoginIdentifier()) from e

        elif password is not None:
            if contact.user and contact.user.check_password(raw_password=password):
                return contact.user

            raise DomainError(InvalidLoginIdentifier())

        if contact.user is None:
            try:
                user = User.objects.create_user(
                    username=generate_unique_username(), password=None
                )
                contact.user = user
                contact.save(update_fields=["user"])

            except IntegrityError as e:
                raise BusinessError(
                    DuplicateResource(resource=_t("User"), field_name=_t("username"))
                ) from e

        return contact.user
