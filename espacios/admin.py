from django.contrib import admin
from .models import Espacio, Horario


class HorarioInline(admin.TabularInline):
    model = Horario
    extra = 1
    fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'activo']


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'capacidad', 'ubicacion', 'estado', 'fecha_creacion']
    list_filter = ['tipo', 'estado']
    search_fields = ['nombre', 'ubicacion']
    inlines = [HorarioInline]
    ordering = ['nombre']


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ['espacio', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo']
    list_filter = ['dia_semana', 'activo', 'espacio']
    search_fields = ['espacio__nombre']
    ordering = ['espacio', 'dia_semana', 'hora_inicio']
