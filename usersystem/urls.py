from django.urls import path, include
from . import views

app_name = 'usersystem'

urlpatterns = [
    path('login',views.login,name='login'),
    path('register',views.register,name='register'),
    path('user/create', views.add_user, name='add_user'),
    path('user/query', views.query_user, name='query_user'),
    path('user/delete', views.delete_user, name='delete_user'),
]