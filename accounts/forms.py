"""
Formularios del módulo de autenticación y usuarios.
Integrante 1 - Sistema de Reservas de Espacios
"""

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.core.exceptions import ValidationError
from .models import CustomUser


class LoginForm(AuthenticationForm):
    """
    Formulario de inicio de sesión personalizado.
    Extiende AuthenticationForm para usar Bootstrap.
    """
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password']


class RegistroForm(UserCreationForm):
    """
    Formulario de registro de nuevos usuarios.
    Incluye campos adicionales del modelo CustomUser.
    """
    first_name = forms.CharField(
        label='Nombre',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre',
        })
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido',
        })
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
        })
    )
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Elige un nombre de usuario',
        })
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de teléfono (opcional)',
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Crea una contraseña segura',
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite la contraseña',
        })
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email',
            'username', 'telefono', 'password1', 'password2'
        ]

    def clean_email(self):
        """Valida que el correo no esté ya registrado."""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_username(self):
        """Valida que el username no contenga caracteres especiales problemáticos."""
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def save(self, commit=True):
        """Guarda el usuario con rol 'usuario' por defecto."""
        user = super().save(commit=False)
        user.rol = CustomUser.ROL_USUARIO
        if commit:
            user.save()
        return user


class PerfilForm(forms.ModelForm):
    """
    Formulario para editar el perfil del usuario autenticado.
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telefono', 'foto_perfil']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono',
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'foto_perfil': 'Foto de perfil',
        }

    def clean_email(self):
        """Valida que el correo no esté en uso por otro usuario."""
        email = self.cleaned_data.get('email')
        usuario_actual = self.instance
        if CustomUser.objects.filter(email=email).exclude(pk=usuario_actual.pk).exists():
            raise ValidationError('Este correo electrónico ya está en uso por otro usuario.')
        return email


class CustomPasswordResetForm(PasswordResetForm):
    """
    Formulario de recuperación de contraseña con estilos Bootstrap.
    """
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu correo registrado',
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """
    Formulario para establecer nueva contraseña con estilos Bootstrap.
    """
    new_password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña',
        })
    )
    new_password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite la nueva contraseña',
        })
    )


class AdminUserForm(forms.ModelForm):
    """
    Formulario para que el administrador gestione usuarios
    (cambiar rol, activar/desactivar cuenta).
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telefono', 'rol', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'rol': 'Rol del usuario',
            'is_active': 'Cuenta activa',
        }
