"""
URLs del módulo de Gestión de Espacios y Horarios.
Integrante 2 - Sistema de Reservas de Espacios
"""

from django.urls import path
from . import views

app_name = 'espacios'

urlpatterns = [
    # ── Espacios ──────────────────────────────────────────────
    path('', views.lista_espacios, name='lista_espacios'),
    path('nuevo/', views.crear_espacio, name='crear_espacio'),
    path('<int:pk>/', views.detalle_espacio, name='detalle_espacio'),
    path('<int:pk>/editar/', views.editar_espacio, name='editar_espacio'),
    path('<int:pk>/eliminar/', views.eliminar_espacio, name='eliminar_espacio'),

    # ── Horarios ──────────────────────────────────────────────
    path('horarios/', views.lista_horarios, name='lista_horarios'),
    path('horarios/nuevo/', views.crear_horario, name='crear_horario'),
    path('<int:espacio_pk>/horarios/nuevo/', views.crear_horario, name='crear_horario_espacio'),
    path('horarios/<int:pk>/editar/', views.editar_horario, name='editar_horario'),
    path('horarios/<int:pk>/eliminar/', views.eliminar_horario, name='eliminar_horario'),

    # ── API JSON (para integración con reservas) ───────────────
    path('api/<int:espacio_pk>/horarios/', views.api_horarios_espacio, name='api_horarios'),
    path('api/disponibles/', views.api_espacios_disponibles, name='api_disponibles'),
]
