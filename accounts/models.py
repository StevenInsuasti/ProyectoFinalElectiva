"""
Modelos del módulo de autenticación y usuarios.
Integrante 1 - Sistema de Reservas de Espacios
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    Agrega campos adicionales como rol, teléfono y foto de perfil.
    """

    # Roles disponibles en el sistema
    ROL_ADMINISTRADOR = 'administrador'
    ROL_USUARIO = 'usuario'

    ROLES = [
        (ROL_ADMINISTRADOR, 'Administrador'),
        (ROL_USUARIO, 'Usuario'),
    ]

    # Campo de rol con valor por defecto 'usuario'
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default=ROL_USUARIO,
        verbose_name='Rol'
    )

    # Teléfono de contacto (opcional)
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )

    # Foto de perfil (opcional)
    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True,
        verbose_name='Foto de perfil'
    )

    # Fecha de última actualización del perfil
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_rol_display()})'

    @property
    def es_administrador(self):
        """Retorna True si el usuario tiene rol de administrador."""
        return self.rol == self.ROL_ADMINISTRADOR

    @property
    def es_usuario(self):
        """Retorna True si el usuario tiene rol de usuario estándar."""
        return self.rol == self.ROL_USUARIO

    def get_nombre_completo(self):
        """Retorna el nombre completo o el username si no tiene nombre."""
        nombre = self.get_full_name()
        return nombre if nombre.strip() else self.username
