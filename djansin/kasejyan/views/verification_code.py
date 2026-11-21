"""Provide the verification-code dispatch endpoint.

Exposes ``VerificationCodeView``, an unauthenticated API view that
accepts a client identifier, delegates code generation and dispatch to
``VerificationCodeService``, and returns an enveloped acknowledgement.
"""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t

from core.permissions.auth_based import AllowAny
from core.views import APIView
from djansin.kasejyan.serializers.verification_code import VerificationCodeSerializer
from djansin.kasejyan.services.verification_code import VerificationCodeService


class VerificationCodeView(APIView):
    """Send a verification code to an unauthenticated client.

    Accepts an identifier (phone or email), delegates dispatch to the
    verification-code service, and returns an empty enveloped response.
    Open to unauthenticated clients.
    """

    permission_classes = [AllowAny]

    def post(self, request: HttpRequest):
        """Handle a verification-code dispatch request.

        Validates the payload and dispatches a code to the submitted
        identifier.

        Args:
            request: The incoming HTTP request carrying the identifier
                payload.

        Returns:
            An enveloped response confirming dispatch.

        Raises:
            ValidationError: When the payload is invalid. Raised by the
                serializer via ``raise_exception=True``.
        """
        serializer = VerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = VerificationCodeService()(serializer.validated_data["identifier"])

        return self.build_response(
            message=_t("Validation code successfully sent."),
            code="VERIFICATION_CODE_SENT",
            data=result.to_dict(),
        )
