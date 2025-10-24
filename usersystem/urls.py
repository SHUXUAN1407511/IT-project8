from django.urls import path

from .views import (
    AdminUserDetailView,
    AdminUserListView,
    AdminUserStatusView,
    LogoutView,
    CurrentUserPasswordView,
    CurrentUserView,
    LoginView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout", LogoutView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/password/reset", PasswordResetRequestView.as_view()),
    path("auth/password/reset/", PasswordResetRequestView.as_view()),
    path("auth/password/reset/confirm", PasswordResetConfirmView.as_view()),
    path("auth/password/reset/confirm/", PasswordResetConfirmView.as_view()),
    path("auth/me", CurrentUserView.as_view()),
    path("auth/me/", CurrentUserView.as_view()),
    path("users/me", CurrentUserView.as_view()),
    path("users/me/", CurrentUserView.as_view()),
    path("users/me/password", CurrentUserPasswordView.as_view()),
    path("users/me/password/", CurrentUserPasswordView.as_view()),
    path("admin/users", AdminUserListView.as_view()),
    path("admin/users/", AdminUserListView.as_view()),
    path("admin/users/<int:user_id>", AdminUserDetailView.as_view()),
    path("admin/users/<int:user_id>/", AdminUserDetailView.as_view()),
    path("admin/users/<int:user_id>/status", AdminUserStatusView.as_view()),
    path("admin/users/<int:user_id>/status/", AdminUserStatusView.as_view()),
]
