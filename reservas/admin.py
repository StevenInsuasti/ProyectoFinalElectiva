"""
Configuración del panel de administración para el módulo de Reservas.
Integrante 3 - Sistema de Reservas de Espacios
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'usuario', 'espacio', 'horario', 'fecha',
        'estado_badge', 'fecha_creacion',
    ]
    list_filter = ['estado', 'fecha', 'espacio', 'confirmacion_automatica']
    search_fields = ['usuario__username', 'usuario__first_name', 'espacio__nombre', 'motivo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    ordering = ['-fecha', '-fecha_creacion']
    date_hierarchy = 'fecha'

    fieldsets = (
        ('Información principal', {
            'fields': ('usuario', 'espacio', 'horario', 'fecha', 'motivo'),
        }),
        ('Estado y control', {
            'fields': ('estado', 'confirmacion_automatica', 'observaciones_admin'),
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def estado_badge(self, obj):
        colores = {
            Reserva.ESTADO_PENDIENTE: 'warning',
            Reserva.ESTADO_APROBADA: 'success',
            Reserva.ESTADO_CANCELADA: 'danger',
        }
        color = colores.get(obj.estado, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_estado_display(),
        )
    estado_badge.short_description = 'Estado'

    actions = ['aprobar_reservas', 'cancelar_reservas']

    def aprobar_reservas(self, request, queryset):
        actualizadas = 0
        for reserva in queryset.filter(estado=Reserva.ESTADO_PENDIENTE):
            try:
                reserva.aprobar()
                actualizadas += 1
            except ValueError:
                pass
        self.message_user(request, f'{actualizadas} reserva(s) aprobada(s).')
    aprobar_reservas.short_description = 'Aprobar reservas seleccionadas'

    def cancelar_reservas(self, request, queryset):
        actualizadas = 0
        for reserva in queryset.exclude(estado=Reserva.ESTADO_CANCELADA):
            try:
                reserva.cancelar()
                actualizadas += 1
            except ValueError:
                pass
        self.message_user(request, f'{actualizadas} reserva(s) cancelada(s).')
    cancelar_reservas.short_description = 'Cancelar reservas seleccionadas'
