from django.contrib import admin
from django.urls import include, path

from usersystem.views import (
    AdminUserDetailView,
    AdminUserListView,
    AdminUserStatusView,
)


# default page:    http://127.0.0.1:8000/
urlpatterns = [
    path('admin/users', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list-slash'),
    path('admin/users/<int:user_id>', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<int:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail-slash'),
    path('admin/users/<int:user_id>/status', AdminUserStatusView.as_view(), name='admin-user-status'),
    path('admin/users/<int:user_id>/status/', AdminUserStatusView.as_view(), name='admin-user-status-slash'),
    path('admin/', admin.site.urls),
    path('api/', include('usersystem.urls')),
    path('', include('AIUseScale.urls')),
    path('', include('Assignment.urls')),
    path('', include('courses.urls')),
]
