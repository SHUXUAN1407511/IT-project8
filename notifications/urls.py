from django.urls import path

from .views import (
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
)

app_name = "notifications"

urlpatterns = [
    path("notifications", NotificationListView.as_view(), name="notifications-list"),
    path("notifications/", NotificationListView.as_view(), name="notifications-list-slash"),
    path(
        "notifications/read-all",
        NotificationMarkAllReadView.as_view(),
        name="notifications-mark-all",
    ),
    path(
        "notifications/read-all/",
        NotificationMarkAllReadView.as_view(),
        name="notifications-mark-all-slash",
    ),
    path(
        "notifications/<uuid:notification_id>/read",
        NotificationMarkReadView.as_view(),
        name="notifications-mark-read",
    ),
    path(
        "notifications/<uuid:notification_id>/read/",
        NotificationMarkReadView.as_view(),
        name="notifications-mark-read-slash",
    ),
]
