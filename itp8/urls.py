from django.contrib import admin
from django.urls import include, path

from usersystem.views import (
    AdminUserDetailView,
    AdminUserListView,
    AdminUserStatusView,
    CurrentUserPasswordView,
    CurrentUserView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
)


# default page:    http://127.0.0.1:8000/
urlpatterns = [
    path('admin/users', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list-slash'),
    path(
        'admin/users/<int:user_id>',
        AdminUserDetailView.as_view(),
        name='admin-user-detail',
    ),
    path(
        'admin/users/<int:user_id>/',
        AdminUserDetailView.as_view(),
        name='admin-user-detail-slash',
    ),
    path(
        'admin/users/<int:user_id>/status',
        AdminUserStatusView.as_view(),
        name='admin-user-status',
    ),
    path(
        'admin/users/<int:user_id>/status/',
        AdminUserStatusView.as_view(),
        name='admin-user-status-slash',
    ),
    path('users/me', CurrentUserView.as_view(), name='current-user-profile'),
    path('users/me/', CurrentUserView.as_view(), name='current-user-profile-slash'),
    path(
        'users/me/password',
        CurrentUserPasswordView.as_view(),
        name='current-user-password',
    ),
    path(
        'users/me/password/',
        CurrentUserPasswordView.as_view(),
        name='current-user-password-slash',
    ),
    path('auth/me', CurrentUserView.as_view(), name='auth-me'),
    path('auth/me/', CurrentUserView.as_view(), name='auth-me-slash'),
    path(
        'auth/password/reset',
        PasswordResetRequestView.as_view(),
        name='password-reset-request',
    ),
    path(
        'auth/password/reset/',
        PasswordResetRequestView.as_view(),
        name='password-reset-request-slash',
    ),
    path(
        'auth/password/reset/confirm',
        PasswordResetConfirmView.as_view(),
        name='password-reset-confirm',
    ),
    path(
        'auth/password/reset/confirm/',
        PasswordResetConfirmView.as_view(),
        name='password-reset-confirm-slash',
    ),
    path('admin/', admin.site.urls),
    path('api/', include('usersystem.urls')),
    path('', include('AIUseScale.urls')),
    path('', include('Assignment.urls')),
    path('', include('courses.urls')),
    path('', include('notifications.urls')),
    path('export/', include('exports.urls')),  # export/excel/ or export/pdf/
]
