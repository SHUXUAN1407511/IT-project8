from django.contrib import admin
from django.urls import path, include


# default page:    http://127.0.0.1:8000/
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('usersystem.urls')),
    path('', include('AIUseScale.urls')),
    path('', include('Assignment.urls')),
    path('', include(('courses.urls', 'courses'), namespace='courses')),
]
