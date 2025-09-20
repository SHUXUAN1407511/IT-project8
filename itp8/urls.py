from django.contrib import admin
from django.urls import path, include
from login import views

# deault page:    http://127.0.0.1:8000/
urlpatterns = [
    path('admin/', admin.site.urls),
    path('info',views.info, name="info"),
    path('register', views.register, name='register'),
    path('if', views.if_view, name='if'),
    path('url', views.url_view, name='url'),
    path('', include('usersystem.urls')),
]
