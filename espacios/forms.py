"""
Formularios validados para Espacios y Horarios.
Integrante 2 - Sistema de Reservas de Espacios
"""

from django import forms
from .models import Espacio, Horario


class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'tipo', 'capacidad', 'ubicacion', 'estado', 'descripcion', 'equipamiento']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: Aula 101'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '1', 'placeholder': 'Número de personas'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: Bloque A, Piso 2'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción opcional...'
            }),
            'equipamiento': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Ej: Proyector, aire acondicionado, 30 sillas'
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError('El nombre no puede estar vacío.')
        # Verificar unicidad excluyendo la instancia actual
        qs = Espacio.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un espacio con este nombre.')
        return nombre

    def clean_capacidad(self):
        capacidad = self.cleaned_data.get('capacidad')
        if capacidad is not None and capacidad < 1:
            raise forms.ValidationError('La capacidad debe ser al menos 1 persona.')
        return capacidad


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['espacio', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo']
        widgets = {
            'espacio': forms.Select(attrs={'class': 'form-select'}),
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control', 'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control', 'type': 'time'
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, espacio=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Si se pasa un espacio fijo (desde la vista de detalle), lo bloqueamos
        if espacio:
            self.fields['espacio'].initial = espacio
            self.fields['espacio'].queryset = Espacio.objects.filter(pk=espacio.pk)
            self.fields['espacio'].widget.attrs['disabled'] = True
        else:
            self.fields['espacio'].queryset = Espacio.objects.filter(
                estado=Espacio.ESTADO_DISPONIBLE
            ).order_by('nombre')

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            self.add_error('hora_fin', 'La hora de fin debe ser posterior a la hora de inicio.')
        return cleaned_data


class FiltroEspacioForm(forms.Form):
    """Formulario de filtros para la lista de espacios."""
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre o ubicación...'
        })
    )
    tipo = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los tipos')] + Espacio.TIPOS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + Espacio.ESTADOS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
