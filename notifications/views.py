from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.responses import error_response

from .models import Notification
from usersystem.permissions import ActiveUserPermission
from .serializers import NotificationSerializer
from .utils import resolve_business_user


class NotificationListView(APIView):
    permission_classes = [ActiveUserPermission]

    def get(self, request):
        user = resolve_business_user(request)
        if not user:
            return error_response(
                "User context not found.", status_code=status.HTTP_404_NOT_FOUND
            )

        queryset = Notification.objects.filter(recipient=user).order_by("-created_at")
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationMarkReadView(APIView):
    permission_classes = [ActiveUserPermission]

    def post(self, request, notification_id):
        user = resolve_business_user(request)
        if not user:
            return error_response(
                "User context not found.", status_code=status.HTTP_404_NOT_FOUND
            )

        try:
            notification = Notification.objects.get(pk=notification_id, recipient=user)
        except Notification.DoesNotExist:
            return error_response(
                "Notification not found.", status_code=status.HTTP_404_NOT_FOUND
            )

        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationMarkAllReadView(APIView):
    permission_classes = [ActiveUserPermission]

    def post(self, request):
        user = resolve_business_user(request)
        if not user:
            return error_response(
                "User context not found.", status_code=status.HTTP_404_NOT_FOUND
            )

        Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
