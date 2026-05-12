"""
Formularios del módulo de Reservas.
Integrante 3 - Sistema de Reservas de Espacios

Usa ModelForms con validaciones robustas en backend y atributos HTML5
para validación en frontend.
"""

from django import forms
from django.utils import timezone

from espacios.models import Espacio, Horario
from .models import Reserva


class ReservaForm(forms.ModelForm):
    """
    Formulario principal para crear y editar reservas.
    Filtra espacios disponibles y horarios activos dinámicamente.
    """

    class Meta:
        model = Reserva
        fields = ['espacio', 'horario', 'fecha', 'motivo']
        widgets = {
            'espacio': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_espacio',
            }),
            'horario': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_horario',
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': str(timezone.localdate()),
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe brevemente el propósito de la reserva...',
            }),
        }
        labels = {
            'espacio': 'Espacio',
            'horario': 'Horario disponible',
            'fecha': 'Fecha de reserva',
            'motivo': 'Motivo (opcional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar espacios disponibles
        self.fields['espacio'].queryset = Espacio.objects.filter(
            estado=Espacio.ESTADO_DISPONIBLE
        ).order_by('nombre')
        self.fields['espacio'].empty_label = '— Selecciona un espacio —'

        # Horarios activos; si hay espacio preseleccionado, filtrar
        if self.instance.pk and self.instance.espacio_id:
            self.fields['horario'].queryset = Horario.objects.filter(
                espacio=self.instance.espacio,
                activo=True,
            ).order_by('dia_semana', 'hora_inicio')
        else:
            self.fields['horario'].queryset = Horario.objects.filter(
                activo=True
            ).select_related('espacio').order_by('espacio__nombre', 'dia_semana', 'hora_inicio')
        self.fields['horario'].empty_label = '— Selecciona un horario —'

        # Marcar campos requeridos visualmente
        self.fields['espacio'].required = True
        self.fields['horario'].required = True
        self.fields['fecha'].required = True

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and not self.instance.pk:
            if fecha < timezone.localdate():
                raise forms.ValidationError('No se pueden crear reservas para fechas pasadas.')
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        espacio = cleaned_data.get('espacio')
        horario = cleaned_data.get('horario')
        fecha = cleaned_data.get('fecha')

        if espacio and horario:
            # Verificar que el horario pertenece al espacio
            if horario.espacio != espacio:
                self.add_error(
                    'horario',
                    'El horario seleccionado no pertenece al espacio elegido.'
                )
                return cleaned_data

            # Verificar que el día de la fecha coincide con el día del horario
            if fecha:
                dia_fecha = fecha.weekday()
                if dia_fecha != horario.dia_semana:
                    nombre_dia = dict(Horario.DIAS_SEMANA).get(horario.dia_semana, '')
                    self.add_error(
                        'fecha',
                        f'La fecha elegida no es {nombre_dia}. '
                        f'El horario seleccionado solo aplica los {nombre_dia}s.'
                    )
                    return cleaned_data

            # Verificar conflictos de horario cruzado
            if fecha:
                conflictos = Reserva.objects.filter(
                    espacio=espacio,
                    fecha=fecha,
                ).exclude(
                    estado=Reserva.ESTADO_CANCELADA
                ).exclude(pk=self.instance.pk if self.instance.pk else None)

                for otra in conflictos:
                    if (
                        horario.hora_inicio < otra.horario.hora_fin
                        and horario.hora_fin > otra.horario.hora_inicio
                    ):
                        self.add_error(
                            'horario',
                            f'Conflicto: "{espacio.nombre}" ya tiene una reserva '
                            f'{otra.get_estado_display().lower()} el {fecha} de '
                            f'{otra.horario.hora_inicio.strftime("%H:%M")} a '
                            f'{otra.horario.hora_fin.strftime("%H:%M")}.'
                        )
                        break

        return cleaned_data


class ReservaAdminForm(forms.ModelForm):
    """
    Formulario extendido para administradores.
    Permite cambiar el estado y agregar observaciones.
    """

    class Meta:
        model = Reserva
        fields = ['espacio', 'horario', 'fecha', 'motivo', 'estado',
                  'observaciones_admin', 'confirmacion_automatica']
        widgets = {
            'espacio': forms.Select(attrs={'class': 'form-select'}),
            'horario': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones_admin': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones internas (opcional)...',
            }),
            'confirmacion_automatica': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['espacio'].queryset = Espacio.objects.all().order_by('nombre')
        self.fields['horario'].queryset = Horario.objects.filter(
            activo=True
        ).select_related('espacio').order_by('espacio__nombre', 'dia_semana', 'hora_inicio')
        self.fields['espacio'].empty_label = '— Selecciona un espacio —'
        self.fields['horario'].empty_label = '— Selecciona un horario —'


class CambiarEstadoForm(forms.Form):
    """
    Formulario simple para que el administrador cambie el estado de una reserva
    con observaciones opcionales.
    """
    ACCIONES = [
        ('aprobar', 'Aprobar'),
        ('cancelar', 'Cancelar'),
    ]

    accion = forms.ChoiceField(
        choices=ACCIONES,
        widget=forms.HiddenInput(),
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones (opcional)...',
        }),
        label='Observaciones',
    )


class FiltroReservaForm(forms.Form):
    """Formulario de filtros para la lista de reservas."""

    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Reserva.ESTADOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        label='Estado',
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-sm',
            'type': 'date',
        }),
        label='Desde',
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-sm',
            'type': 'date',
        }),
        label='Hasta',
    )
    espacio = forms.ModelChoiceField(
        queryset=Espacio.objects.all().order_by('nombre'),
        required=False,
        empty_label='Todos los espacios',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        label='Espacio',
    )
