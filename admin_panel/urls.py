from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.users_list, name='users_list'),
    path('users/toggle/<int:user_id>/', views.toggle_user, name='toggle_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('scans/', views.all_scans, name='all_scans'),
    path('keywords/', views.keywords, name='keywords'),
    path('export/', views.export_csv, name='export_csv'),
]
