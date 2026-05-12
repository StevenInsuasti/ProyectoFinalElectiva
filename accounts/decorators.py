"""
Decoradores personalizados para control de acceso por rol.
Integrante 1 - Sistema de Reservas de Espacios
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def administrador_requerido(view_func):
    """
    Decorador que restringe el acceso solo a usuarios con rol 'administrador'.
    Redirige a dashboard si el usuario no tiene permisos.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.es_administrador:
            messages.error(
                request,
                'No tienes permisos para acceder a esta sección. '
                'Se requiere rol de Administrador.'
            )
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def usuario_requerido(view_func):
    """
    Decorador que permite acceso a usuarios autenticados (cualquier rol).
    Equivalente a @login_required pero con mensaje personalizado.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(
                request,
                'Debes iniciar sesión para acceder a esta página.'
            )
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper
