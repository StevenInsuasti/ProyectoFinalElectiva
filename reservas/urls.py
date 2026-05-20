"""
URLs del módulo de Reservas.
Integrante 3 - Sistema de Reservas de Espacios
"""

from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    # ── Lista y detalle ──────────────────────────────────────────────────────
    path('', views.lista_reservas, name='lista_reservas'),
    path('<int:pk>/', views.detalle_reserva, name='detalle_reserva'),

    # ── CRUD ─────────────────────────────────────────────────────────────────
    path('nueva/', views.crear_reserva, name='crear_reserva'),
    path('<int:pk>/editar/', views.editar_reserva, name='editar_reserva'),
    path('<int:pk>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    path('<int:pk>/eliminar/', views.eliminar_reserva, name='eliminar_reserva'),

    # ── Acciones de estado (admin) ───────────────────────────────────────────
    path('<int:pk>/estado/', views.cambiar_estado_reserva, name='cambiar_estado'),

    # ── Historial del usuario ────────────────────────────────────────────────
    path('historial/', views.historial_reservas, name='historial_reservas'),

    # ── Panel admin ──────────────────────────────────────────────────────────
    path('admin/panel/', views.panel_admin_reservas, name='panel_admin'),

    # ── API JSON ─────────────────────────────────────────────────────────────
    path('api/horarios/<int:espacio_pk>/', views.api_horarios_disponibles, name='api_horarios'),
]
