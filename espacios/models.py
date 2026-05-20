"""
Modelos del módulo de Gestión de Espacios y Horarios.
Integrante 2 - Sistema de Reservas de Espacios

Modelos:
    - Espacio: representa un espacio físico reservable (aula, laboratorio, sala, etc.)
    - Horario: define un bloque de tiempo disponible asociado a un espacio
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Espacio(models.Model):
    """
    Representa un espacio físico reservable dentro de la institución.

    Tipos soportados: aula, laboratorio, sala de reuniones, auditorio, otro.
    Estados posibles: disponible, en mantenimiento, inactivo.
    """

    # ── Constantes de tipo ────────────────────────────────────────────────────
    TIPO_AULA = 'aula'
    TIPO_LABORATORIO = 'laboratorio'
    TIPO_SALA = 'sala'
    TIPO_AUDITORIO = 'auditorio'
    TIPO_OTRO = 'otro'

    TIPOS = [
        (TIPO_AULA, 'Aula'),
        (TIPO_LABORATORIO, 'Laboratorio'),
        (TIPO_SALA, 'Sala de Reuniones'),
        (TIPO_AUDITORIO, 'Auditorio'),
        (TIPO_OTRO, 'Otro'),
    ]

    # ── Constantes de estado ──────────────────────────────────────────────────
    ESTADO_DISPONIBLE = 'disponible'
    ESTADO_MANTENIMIENTO = 'mantenimiento'
    ESTADO_INACTIVO = 'inactivo'

    ESTADOS = [
        (ESTADO_DISPONIBLE, 'Disponible'),
        (ESTADO_MANTENIMIENTO, 'En Mantenimiento'),
        (ESTADO_INACTIVO, 'Inactivo'),
    ]

    # ── Campos ────────────────────────────────────────────────────────────────
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    tipo = models.CharField(max_length=20, choices=TIPOS, default=TIPO_AULA, verbose_name='Tipo')
    capacidad = models.PositiveIntegerField(verbose_name='Capacidad (personas)')
    ubicacion = models.CharField(max_length=200, verbose_name='Ubicación')
    estado = models.CharField(
        max_length=20, choices=ESTADOS, default=ESTADO_DISPONIBLE, verbose_name='Estado'
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    equipamiento = models.TextField(
        blank=True, null=True,
        verbose_name='Equipamiento',
        help_text='Ej: proyector, aire acondicionado, pizarrón'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_display()}) — Cap. {self.capacidad}'

    @property
    def esta_disponible(self):
        """Retorna True si el espacio está en estado disponible."""
        return self.estado == self.ESTADO_DISPONIBLE

    def get_horarios_activos(self):
        """Retorna los horarios activos asociados a este espacio."""
        return self.horarios.filter(activo=True)


class Horario(models.Model):
    """
    Define un bloque de tiempo disponible para un espacio.
    Preparado para integrarse con el módulo de Reservas (Integrante 3).
    """

    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.CASCADE,
        related_name='horarios',
        verbose_name='Espacio'
    )
    dia_semana = models.IntegerField(choices=DIAS_SEMANA, verbose_name='Día de la semana')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin = models.TimeField(verbose_name='Hora de fin')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        ordering = ['espacio', 'dia_semana', 'hora_inicio']
        # Evitar duplicados: mismo espacio, mismo día, misma hora de inicio
        unique_together = [('espacio', 'dia_semana', 'hora_inicio')]

    def __str__(self):
        return (
            f'{self.espacio.nombre} — {self.get_dia_semana_display()} '
            f'{self.hora_inicio.strftime("%H:%M")} a {self.hora_fin.strftime("%H:%M")}'
        )

    def clean(self):
        """Validar que hora_fin sea posterior a hora_inicio."""
        if self.hora_inicio and self.hora_fin:
            if self.hora_fin <= self.hora_inicio:
                raise ValidationError(
                    {'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'}
                )
        # Validar solapamiento con otros horarios del mismo espacio y día
        if self.espacio_id and self.dia_semana is not None:
            qs = Horario.objects.filter(
                espacio=self.espacio_id,
                dia_semana=self.dia_semana,
                activo=True,
            ).exclude(pk=self.pk)
            for h in qs:
                if self.hora_inicio < h.hora_fin and self.hora_fin > h.hora_inicio:
                    raise ValidationError(
                        'Este horario se solapa con otro horario existente para el mismo espacio y día.'
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duracion_minutos(self):
        from datetime import datetime, date
        inicio = datetime.combine(date.today(), self.hora_inicio)
        fin = datetime.combine(date.today(), self.hora_fin)
        return int((fin - inicio).total_seconds() / 60)
