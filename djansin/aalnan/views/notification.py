"""Views for the ``aalnan`` app."""

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _t
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status

from core.exceptions import BusinessError
from core.exceptions.errors.business import ResourceNotFound
from core.permissions.auth_based import IsAuthenticated
from core.views import APIView, Response
from djansin.aalnan.models import Notification
from djansin.aalnan.serializers.notification import NotificationListEnvelopeSerializer
from djansin.aalnan.types import NotificationListResult
from djansin.kasejyan.serializers.error import ErrorEnvelopeSerializer


class NotificationListView(APIView):
    """List the authenticated user's notifications."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List notifications",
        description="Returns the authenticated user's notifications, newest first.",
        parameters=[
            OpenApiParameter(
                name="unread_only",
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description="If true, return only unread notifications.",
            ),
        ],
        responses={
            200: NotificationListEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
        },
        tags=["Aalnan"],
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        qs = Notification.objects.for_user(request.user).newest_first()

        unread_only = request.query_params.get("unread_only", "").lower()
        if unread_only in {"1", "true", "yes"}:
            qs = qs.unread()

        unread_count = Notification.objects.unread_for_user(request.user).count()
        results = [
            {
                "id": n.pk,
                "type": n.type,
                "title": n.title,
                "body": n.body,
                "data": n.data,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in qs
        ]

        payload = NotificationListResult(
            count=len(results),
            unread_count=unread_count,
            results=[],  # not used; kept for type symmetry
        )

        return self.build_response(
            message=_t("Notifications retrieved successfully."),
            code="NOTIFICATIONS_LISTED",
            data={
                "count": payload.count,
                "unread_count": payload.unread_count,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class NotificationReadView(APIView):
    """Mark a single notification as read."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Mark a notification as read",
        responses={
            200: NotificationListEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            404: ErrorEnvelopeSerializer,
        },
        tags=["Aalnan"],
    )
    def patch(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        notification = Notification.objects.for_user(request.user).filter(pk=pk).first()
        if notification is None:
            raise BusinessError(ResourceNotFound(resource=_t("Notification")))

        notification.mark_read()

        return self.build_response(
            message=_t("Notification marked as read."),
            code="NOTIFICATION_READ",
            data={
                "id": notification.pk,
                "is_read": notification.is_read,
            },
            status=status.HTTP_200_OK,
        )


class NotificationReadAllView(APIView):
    """Mark every notification of the user as read."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Mark all notifications as read",
        responses={
            200: NotificationListEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
        },
        tags=["Aalnan"],
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        updated = (
            Notification.objects.for_user(request.user).unread().update(is_read=True)
        )

        return self.build_response(
            message=_t("All notifications marked as read."),
            code="NOTIFICATIONS_READ_ALL",
            data={"updated": updated},
            status=status.HTTP_200_OK,
        )


class NotificationDeleteView(APIView):
    """Delete a single notification."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Delete a notification",
        responses={
            200: NotificationListEnvelopeSerializer,
            401: ErrorEnvelopeSerializer,
            404: ErrorEnvelopeSerializer,
        },
        tags=["Aalnan"],
    )
    def delete(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        notification = Notification.objects.for_user(request.user).filter(pk=pk).first()
        if notification is None:
            raise BusinessError(ResourceNotFound(resource=_t("Notification")))

        notification.delete()

        return self.build_response(
            message=_t("Notification deleted."),
            code="NOTIFICATION_DELETED",
            data={"id": pk},
            status=status.HTTP_200_OK,
        )
