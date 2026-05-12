"""
Vistas del módulo de autenticación y usuarios.
Integrante 1 - Sistema de Reservas de Espacios

Incluye: login, registro, logout, dashboard, perfil,
         gestión de usuarios (admin) y recuperación de contraseña.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models import Q

from .models import CustomUser
from .forms import (
    LoginForm,
    RegistroForm,
    PerfilForm,
    AdminUserForm,
)
from .decorators import administrador_requerido


# ─────────────────────────────────────────────
#  AUTENTICACIÓN
# ─────────────────────────────────────────────

def login_view(request):
    """
    Vista de inicio de sesión.
    Redirige al dashboard si el usuario ya está autenticado.
    """
    # Si ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(
                        request,
                        f'¡Bienvenido, {user.get_nombre_completo()}!'
                    )
                    # Redirigir a la URL solicitada o al dashboard
                    next_url = request.GET.get('next', 'accounts:dashboard')
                    return redirect(next_url)
                else:
                    messages.error(
                        request,
                        'Tu cuenta está desactivada. Contacta al administrador.'
                    )
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def registro_view(request):
    """
    Vista de registro de nuevos usuarios.
    Solo permite registro si no está autenticado.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciar sesión automáticamente tras el registro
            login(request, user)
            messages.success(
                request,
                f'¡Cuenta creada exitosamente! Bienvenido, {user.get_nombre_completo()}.'
            )
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroForm()

    return render(request, 'accounts/registro.html', {'form': form})


@login_required
def logout_view(request):
    """
    Vista de cierre de sesión.
    Solo acepta POST para evitar logout accidental por GET.
    """
    if request.method == 'POST':
        nombre = request.user.get_nombre_completo()
        logout(request)
        messages.info(request, f'Has cerrado sesión. ¡Hasta pronto, {nombre}!')
    return redirect('accounts:login')


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────

@login_required
def dashboard_view(request):
    """
    Dashboard principal del usuario autenticado.
    Muestra información diferente según el rol.
    """
    context = {
        'usuario': request.user,
    }

    # Si es administrador, agregar estadísticas de usuarios
    if request.user.es_administrador:
        context['total_usuarios'] = CustomUser.objects.count()
        context['usuarios_activos'] = CustomUser.objects.filter(is_active=True).count()
        context['total_admins'] = CustomUser.objects.filter(
            rol=CustomUser.ROL_ADMINISTRADOR
        ).count()
        context['ultimos_usuarios'] = CustomUser.objects.order_by('-date_joined')[:5]

        # Estadísticas de espacios (Integrante 2)
        try:
            from espacios.models import Espacio
            context['total_espacios'] = Espacio.objects.count()
            context['espacios_disponibles'] = Espacio.objects.filter(
                estado=Espacio.ESTADO_DISPONIBLE
            ).count()
        except Exception:
            context['total_espacios'] = None
            context['espacios_disponibles'] = None

    return render(request, 'accounts/dashboard.html', context)


# ─────────────────────────────────────────────
#  PERFIL DE USUARIO
# ─────────────────────────────────────────────

@login_required
def perfil_view(request):
    """
    Vista para ver y editar el perfil del usuario autenticado.
    """
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('accounts:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = PerfilForm(instance=request.user)

    return render(request, 'accounts/perfil.html', {'form': form})


@login_required
def cambiar_password_view(request):
    """
    Vista para cambiar la contraseña del usuario autenticado.
    Mantiene la sesión activa tras el cambio.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Actualizar hash de sesión para no cerrar sesión
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('accounts:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = PasswordChangeForm(request.user)
        # Aplicar clases Bootstrap a los campos
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'

    return render(request, 'accounts/cambiar_password.html', {'form': form})


# ─────────────────────────────────────────────
#  GESTIÓN DE USUARIOS (SOLO ADMINISTRADOR)
# ─────────────────────────────────────────────

@administrador_requerido
def lista_usuarios_view(request):
    """
    Vista para listar todos los usuarios del sistema.
    Solo accesible para administradores.
    Incluye búsqueda por nombre, username o email.
    """
    query = request.GET.get('q', '')
    usuarios = CustomUser.objects.all().order_by('username')

    # Filtro de búsqueda
    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'usuarios': usuarios,
        'query': query,
        'total': usuarios.count(),
    }
    return render(request, 'accounts/lista_usuarios.html', context)


@administrador_requerido
def editar_usuario_view(request, pk):
    """
    Vista para que el administrador edite un usuario específico.
    Permite cambiar rol, datos personales y estado de la cuenta.
    """
    usuario = get_object_or_404(CustomUser, pk=pk)

    # Evitar que el admin se edite a sí mismo desde aquí
    if usuario == request.user:
        messages.warning(
            request,
            'Para editar tu propio perfil, usa la sección "Mi Perfil".'
        )
        return redirect('accounts:lista_usuarios')

    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Usuario {usuario.username} actualizado correctamente.'
            )
            return redirect('accounts:lista_usuarios')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = AdminUserForm(instance=usuario)

    return render(request, 'accounts/editar_usuario.html', {
        'form': form,
        'usuario': usuario,
    })


@administrador_requerido
def toggle_usuario_view(request, pk):
    """
    Vista para activar/desactivar una cuenta de usuario.
    Solo acepta POST para evitar cambios accidentales.
    """
    if request.method == 'POST':
        usuario = get_object_or_404(CustomUser, pk=pk)

        # No permitir desactivar la propia cuenta
        if usuario == request.user:
            messages.error(request, 'No puedes desactivar tu propia cuenta.')
            return redirect('accounts:lista_usuarios')

        usuario.is_active = not usuario.is_active
        usuario.save()

        estado = 'activada' if usuario.is_active else 'desactivada'
        messages.success(
            request,
            f'Cuenta de {usuario.username} {estado} correctamente.'
        )

    return redirect('accounts:lista_usuarios')


@administrador_requerido
def detalle_usuario_view(request, pk):
    """
    Vista de detalle de un usuario para el administrador.
    """
    usuario = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'accounts/detalle_usuario.html', {'usuario': usuario})
