"""Views for the ``aalnan`` app."""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import extend_schema
from rest_framework import status

from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.aalnan.serializers.notification import (
    NotificationPreferenceEnvelopeSerializer,
)
from djansin.aalnan.serializers.preference import UpdateNotificationPreferenceSerializer
from djansin.aalnan.services.preferences import (
    GetNotificationPreferenceService,
    UpdateNotificationPreferenceService,
)
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer


class NotificationPreferenceView(APIView):
    """Read or update the user's notification preferences."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get notification preferences",
        responses={
            200: NotificationPreferenceEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
        },
        tags=["Aalnan"],
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        result = GetNotificationPreferenceService()(user=request.user)
        return self.build_response(
            message=_t("Preferences retrieved."),
            code="NOTIFICATION_PREFERENCES_RETRIEVED",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update notification preferences",
        request=UpdateNotificationPreferenceSerializer,
        responses={
            200: NotificationPreferenceEnvelopeSerializer,
            400: ErrorEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
        },
        tags=["Aalnan"],
    )
    def patch(self, request: HttpRequest, *args, **kwargs) -> Response:
        serializer = UpdateNotificationPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = UpdateNotificationPreferenceService()(
            user=request.user,
            in_app_enabled=serializer.validated_data.get("in_app_enabled"),
            email_enabled=serializer.validated_data.get("email_enabled"),
            sms_enabled=serializer.validated_data.get("sms_enabled"),
        )

        return self.build_response(
            message=_t("Preferences updated."),
            code="NOTIFICATION_PREFERENCES_UPDATED",
            data=result.to_dict(),
            status=status.HTTP_200_OK,
        )
