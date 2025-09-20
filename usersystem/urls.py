from django.urls import path, include
from usersystem import views

app_name = 'usersystem'

urlpatterns = [
    path('login',views.login,name='login'),
    path('register',views.register,name='register'),
]