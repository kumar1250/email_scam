from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', lambda request: redirect('accounts:login'), name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('scanner/', include('scanner.urls', namespace='scanner')),
    path('admin-panel/', include('admin_panel.urls', namespace='admin_panel')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
