from django.urls import path
from . import views

app_name = 'scanner'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('scan/', views.scan_email, name='scan_email'),
    path('history/', views.history, name='history'),
    path('detail/<int:scan_id>/', views.scan_detail, name='scan_detail'),
    path('delete/<int:scan_id>/', views.delete_scan, name='delete_scan'),
    path('delete-all/', views.delete_all_history, name='delete_all_history'),
    path('export/', views.export_history_csv, name='export_history_csv'),
]
