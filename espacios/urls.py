"""
URLs del módulo de Gestión de Espacios y Horarios.
Integrante 2 - Sistema de Reservas de Espacios

Rutas de Espacios:
    /espacios/                      -> lista_espacios
    /espacios/nuevo/                -> crear_espacio (admin)
    /espacios/<pk>/                 -> detalle_espacio
    /espacios/<pk>/editar/          -> editar_espacio (admin)
    /espacios/<pk>/eliminar/        -> eliminar_espacio (admin)

Rutas de Horarios:
    /espacios/horarios/             -> lista_horarios
    /espacios/horarios/nuevo/       -> crear_horario (admin)
    /espacios/<pk>/horarios/nuevo/  -> crear_horario_espacio (admin)
    /espacios/horarios/<pk>/editar/ -> editar_horario (admin)
    /espacios/horarios/<pk>/eliminar/ -> eliminar_horario (admin)

Rutas API JSON:
    /espacios/api/<pk>/horarios/    -> api_horarios_espacio
    /espacios/api/disponibles/      -> api_espacios_disponibles
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
