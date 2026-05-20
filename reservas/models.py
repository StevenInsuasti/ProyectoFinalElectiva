"""
Modelos del módulo de Reservas.
Integrante 3 - Sistema de Reservas de Espacios

Gestiona el ciclo completo de una reserva: creación, validación de conflictos,
estados (pendiente / aprobada / cancelada) e historial por usuario.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from espacios.models import Espacio, Horario


class Reserva(models.Model):
    """
    Representa una reserva de un espacio en un horario específico para una fecha concreta.

    Relaciones:
        - usuario  → settings.AUTH_USER_MODEL (CustomUser)
        - espacio  → espacios.Espacio
        - horario  → espacios.Horario
    """

    # ── Estados ──────────────────────────────────────────────────────────────
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADA = 'aprobada'
    ESTADO_CANCELADA = 'cancelada'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_APROBADA, 'Aprobada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]

    # ── Campos ───────────────────────────────────────────────────────────────
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Usuario',
    )
    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Espacio',
    )
    horario = models.ForeignKey(
        Horario,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Horario',
    )
    fecha = models.DateField(verbose_name='Fecha de reserva')
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
        verbose_name='Estado',
    )
    motivo = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo / Descripción',
        help_text='Describe brevemente el propósito de la reserva.',
    )
    observaciones_admin = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones del administrador',
        help_text='Notas internas del administrador al aprobar o cancelar.',
    )
    confirmacion_automatica = models.BooleanField(
        default=False,
        verbose_name='Confirmación automática',
        help_text='Si está activo, la reserva se aprueba automáticamente al crearse.',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    # ── Meta ─────────────────────────────────────────────────────────────────
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha', '-fecha_creacion']
        # Evitar doble reserva exacta: mismo espacio + horario + fecha
        unique_together = [('espacio', 'horario', 'fecha')]

    def __str__(self):
        return (
            f'Reserva #{self.pk} — {self.espacio.nombre} | '
            f'{self.fecha} {self.horario.hora_inicio.strftime("%H:%M")} | '
            f'{self.get_estado_display()}'
        )

    # ── Propiedades ──────────────────────────────────────────────────────────
    @property
    def esta_pendiente(self):
        return self.estado == self.ESTADO_PENDIENTE

    @property
    def esta_aprobada(self):
        return self.estado == self.ESTADO_APROBADA

    @property
    def esta_cancelada(self):
        return self.estado == self.ESTADO_CANCELADA

    @property
    def es_futura(self):
        """Retorna True si la reserva es para una fecha futura o de hoy."""
        return self.fecha >= timezone.localdate()

    @property
    def puede_cancelarse(self):
        """El usuario puede cancelar si está pendiente o aprobada y es futura."""
        return self.estado in (self.ESTADO_PENDIENTE, self.ESTADO_APROBADA) and self.es_futura

    # ── Validaciones ─────────────────────────────────────────────────────────
    def clean(self):
        errors = {}

        # 1. El horario debe pertenecer al espacio seleccionado
        if self.horario_id and self.espacio_id:
            if self.horario.espacio_id != self.espacio_id:
                errors['horario'] = (
                    'El horario seleccionado no pertenece al espacio elegido.'
                )

        # 2. El horario debe estar activo
        if self.horario_id and not self.horario.activo:
            errors['horario'] = 'El horario seleccionado no está activo.'

        # 3. El espacio debe estar disponible
        if self.espacio_id and self.espacio.estado != Espacio.ESTADO_DISPONIBLE:
            errors['espacio'] = (
                f'El espacio "{self.espacio.nombre}" no está disponible '
                f'(estado: {self.espacio.get_estado_display()}).'
            )

        # 4. La fecha no puede ser en el pasado (solo al crear)
        if self.fecha and not self.pk:
            if self.fecha < timezone.localdate():
                errors['fecha'] = 'No se pueden crear reservas para fechas pasadas.'

        # 5. El día de la semana de la fecha debe coincidir con el día del horario
        if self.fecha and self.horario_id:
            dia_fecha = self.fecha.weekday()  # 0=Lunes … 6=Domingo
            if dia_fecha != self.horario.dia_semana:
                nombre_dia = dict(Horario.DIAS_SEMANA).get(self.horario.dia_semana, '')
                errors['fecha'] = (
                    f'La fecha seleccionada no corresponde al día del horario '
                    f'({nombre_dia}). Elige una fecha que caiga en {nombre_dia}.'
                )

        # 6. Detectar conflictos de horario cruzado en el mismo espacio y fecha
        if self.espacio_id and self.fecha and self.horario_id and not errors.get('horario'):
            conflictos = Reserva.objects.filter(
                espacio=self.espacio_id,
                fecha=self.fecha,
            ).exclude(
                estado=self.ESTADO_CANCELADA
            ).exclude(pk=self.pk)

            for otra in conflictos:
                # Verificar solapamiento de horarios
                if (
                    self.horario.hora_inicio < otra.horario.hora_fin
                    and self.horario.hora_fin > otra.horario.hora_inicio
                ):
                    errors['horario'] = (
                        f'Conflicto de horario: el espacio "{self.espacio.nombre}" '
                        f'ya tiene una reserva {otra.get_estado_display().lower()} '
                        f'el {otra.fecha} de '
                        f'{otra.horario.hora_inicio.strftime("%H:%M")} a '
                        f'{otra.horario.hora_fin.strftime("%H:%M")}.'
                    )
                    break

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Aplicar confirmación automática al crear
        if not self.pk and self.confirmacion_automatica:
            self.estado = self.ESTADO_APROBADA
        self.full_clean()
        super().save(*args, **kwargs)

    # ── Métodos de negocio ───────────────────────────────────────────────────
    def aprobar(self, observaciones=''):
        """Aprueba la reserva. Solo válido si está pendiente."""
        if self.estado != self.ESTADO_PENDIENTE:
            raise ValueError('Solo se pueden aprobar reservas en estado pendiente.')
        self.estado = self.ESTADO_APROBADA
        if observaciones:
            self.observaciones_admin = observaciones
        self.save(update_fields=['estado', 'observaciones_admin', 'fecha_actualizacion'])

    def cancelar(self, observaciones=''):
        """Cancela la reserva. Válido si está pendiente o aprobada."""
        if self.estado == self.ESTADO_CANCELADA:
            raise ValueError('La reserva ya está cancelada.')
        self.estado = self.ESTADO_CANCELADA
        if observaciones:
            self.observaciones_admin = observaciones
        self.save(update_fields=['estado', 'observaciones_admin', 'fecha_actualizacion'])
