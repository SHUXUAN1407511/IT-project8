from django.contrib import admin
from django.urls import path, include
from book import views1
from usersystem import views

# deault page:    http://127.0.0.1:8000/
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usersystem.urls')),
    path('register', views.register, name='register'),
    path('book', views1.add_book,name='add_book'),
    path('book/query', views1.query_book,name='query_book'),
]
