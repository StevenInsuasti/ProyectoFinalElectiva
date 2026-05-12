"""
URLs principales del proyecto Sistema de Reservas de Espacios.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Módulo de autenticación y usuarios (Integrante 1)
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Redirección raíz al login
    path('', lambda request: redirect('accounts:login'), name='home'),
]

# Servir archivos de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
