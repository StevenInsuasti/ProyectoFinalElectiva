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

    # Módulo de Gestión de Espacios y Horarios (Integrante 2)
    path('espacios/', include('espacios.urls', namespace='espacios')),

    # Módulo de Reservas (Integrante 3)
    path('reservas/', include('reservas.urls', namespace='reservas')),

    # Dashboard analítico, exportaciones y calendario (Integrante 4)
    path('reporting/', include('reporting.urls', namespace='reporting')),

    # Redirección raíz al login
    path('', lambda request: redirect('accounts:login'), name='home'),
]

# Servir archivos de medios en desarrollo y producción
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
