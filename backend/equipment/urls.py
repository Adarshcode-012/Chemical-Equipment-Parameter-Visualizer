from django.urls import path
from .views import UploadCSVView, HistoryView, ReportView

urlpatterns = [
    path('upload/', UploadCSVView.as_view(), name='upload'),
    path('history/', HistoryView.as_view(), name='history'),
    path('report/', ReportView.as_view(), name='report'),
]
