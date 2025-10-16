from django.urls import path
from .views import ExportExcelView, ExportPDFView

urlpatterns = [
    path('excel/', ExportExcelView.as_view(), name='export-excel'),
    path('pdf/', ExportPDFView.as_view(), name='export-pdf'),
]
