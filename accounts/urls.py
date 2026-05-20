"""
URLs del módulo de autenticación y usuarios.
Integrante 1 - Sistema de Reservas de Espacios
"""

from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

app_name = 'accounts'

urlpatterns = [
    # ── Autenticación ──────────────────────────────────────────
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # ── Dashboard ──────────────────────────────────────────────
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # ── Perfil del usuario autenticado ─────────────────────────
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/cambiar-password/', views.cambiar_password_view, name='cambiar_password'),

    # ── Gestión de usuarios (solo administrador) ───────────────
    path('usuarios/', views.lista_usuarios_view, name='lista_usuarios'),
    path('usuarios/<int:pk>/', views.detalle_usuario_view, name='detalle_usuario'),
    path('usuarios/<int:pk>/editar/', views.editar_usuario_view, name='editar_usuario'),
    path('usuarios/<int:pk>/toggle/', views.toggle_usuario_view, name='toggle_usuario'),

    # ── Recuperación de contraseña (vistas integradas de Django) ─
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            form_class=CustomPasswordResetForm,
            email_template_name='accounts/emails/password_reset_email.html',
            subject_template_name='accounts/emails/password_reset_subject.txt',
            success_url='/accounts/password-reset/done/',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            form_class=CustomSetPasswordForm,
            success_url='/accounts/password-reset/complete/',
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]
