"""Provide the verification-code dispatch endpoint.

Exposes ``VerificationCodeView``, an unauthenticated API view that
accepts a client identifier, delegates code generation and dispatch to
``VerificationCodeService``, and returns an enveloped acknowledgement.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import AllowAny
from core.views import APIView
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer
from djansin.kasejyan.serializers.verification_code import (
    CodeDispatchEnvelopeSerializer,
    VerificationCodeSerializer,
)
from djansin.kasejyan.services.verification_code import VerificationCodeService


class VerificationCodeView(APIView):
    """Send a verification code to an unauthenticated client.

    Accepts an identifier (phone or email), delegates dispatch to the
    verification-code service, and returns an enveloped response
    describing the dispatch channel. Open to unauthenticated clients.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Dispatch a verification code",
        description=(
            "Dispatches a six-digit verification code to the supplied "
            "identifier (email or phone). The code is issued with "
            "``purpose=CodePurpose.AUTHENTICATE``, so it can only be "
            "used to complete a passwordless sign-in. Blocked contacts "
            "are rejected before a code is issued. Open to "
            "unauthenticated clients."
        ),
        request=VerificationCodeSerializer,
        responses={
            200: CodeDispatchEnvelopeSerializer,
            422: ErrorEnvelopeSerializer,
        },
        tags=["Kasejyan"],
    )
    def post(self, request: HttpRequest):
        """Handle a verification-code dispatch request.

        Validates the payload and dispatches a code to the submitted
        identifier.

        Args:
            request: The incoming HTTP request carrying the identifier
                payload.

        Returns:
            An enveloped response confirming dispatch, including the
            contact type (``"email"`` or ``"phone"``) and the
            destination identifier.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
            BusinessError: When the contact is temporarily blocked or
                a still-valid code is already outstanding. Raised by
                the service layer.
        """
        serializer = VerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = VerificationCodeService()(serializer.validated_data["identifier"])

        return self.build_response(
            message=_t("Validation code successfully sent."),
            code="VERIFICATION_CODE_SENT",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )
