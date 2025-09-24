from django.urls import path, include
from . import views

app_name = 'Assignment'

urlpatterns = [
    path('Assignment', views.create_assignment, name='create_assignment'),
    path('Assignment/query', views.query_assignment, name='query_assignment'),
    path('Assignment/AIUseScale', views.AIUseScale, name='AIUseScale'),
]