"""
Configuración del panel de administración de Django para el módulo de usuarios.
Integrante 1 - Sistema de Reservas de Espacios
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuración del admin para el modelo CustomUser.
    Extiende UserAdmin para incluir los campos personalizados.
    """

    # Columnas visibles en la lista de usuarios
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'rol', 'is_active', 'date_joined'
    ]

    # Filtros laterales
    list_filter = ['rol', 'is_active', 'is_staff', 'date_joined']

    # Campos de búsqueda
    search_fields = ['username', 'email', 'first_name', 'last_name']

    # Ordenamiento por defecto
    ordering = ['username']

    # Campos editables directamente en la lista
    list_editable = ['rol', 'is_active']

    # Secciones del formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'telefono', 'foto_perfil')
        }),
    )

    # Secciones del formulario de creación
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('first_name', 'last_name', 'email', 'rol', 'telefono')
        }),
    )
