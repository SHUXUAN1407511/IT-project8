from django.urls import path
from .views import RegisterView, LoginView  # 按你的 app 名称调整

urlpatterns = [
    path("api/register", RegisterView.as_view()),
    path("api/login", LoginView.as_view()),
]
