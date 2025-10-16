from django.urls import path

from .views import (
    AdminUserDetailView,
    AdminUserListView,
    AdminUserStatusView,
    LoginView,
    RegisterView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("admin/users", AdminUserListView.as_view()),
    path("admin/users/", AdminUserListView.as_view()),
    path("admin/users/<int:user_id>", AdminUserDetailView.as_view()),
    path("admin/users/<int:user_id>/", AdminUserDetailView.as_view()),
    path("admin/users/<int:user_id>/status", AdminUserStatusView.as_view()),
    path("admin/users/<int:user_id>/status/", AdminUserStatusView.as_view()),
]
