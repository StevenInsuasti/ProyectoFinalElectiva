"""URLs del módulo de reportes — Integrante 4."""

from django.urls import path

from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('export/pdf/', views.export_reservas_pdf, name='export_pdf'),
    path('export/excel/', views.export_reservas_excel, name='export_excel'),
    path('api/calendar-events/', views.calendar_events_api, name='calendar_events'),
]
