"""
Comando para agregar horarios de lunes a viernes a todos los espacios disponibles.
Se ejecuta en el buildCommand de Render para garantizar que los horarios
existan aunque los espacios ya hayan sido creados previamente.

Uso:
    python manage.py seed_horarios

Usa get_or_create para evitar duplicados si se ejecuta más de una vez.
"""

from datetime import time
from django.core.management.base import BaseCommand
from espacios.models import Espacio, Horario


# Franjas horarias de 2 horas, lunes (0) a viernes (4)
HORARIOS_BASE = [
    (0, '07:00', '09:00'),
    (0, '09:00', '11:00'),
    (0, '11:00', '13:00'),
    (0, '14:00', '16:00'),
    (0, '16:00', '18:00'),
    (1, '07:00', '09:00'),
    (1, '09:00', '11:00'),
    (1, '11:00', '13:00'),
    (1, '14:00', '16:00'),
    (1, '16:00', '18:00'),
    (2, '07:00', '09:00'),
    (2, '09:00', '11:00'),
    (2, '11:00', '13:00'),
    (2, '14:00', '16:00'),
    (2, '16:00', '18:00'),
    (3, '07:00', '09:00'),
    (3, '09:00', '11:00'),
    (3, '11:00', '13:00'),
    (3, '14:00', '16:00'),
    (3, '16:00', '18:00'),
    (4, '07:00', '09:00'),
    (4, '09:00', '11:00'),
    (4, '11:00', '13:00'),
    (4, '14:00', '16:00'),
    (4, '16:00', '18:00'),
]


class Command(BaseCommand):
    help = 'Agrega horarios L-V a todos los espacios disponibles (sin duplicados)'

    def handle(self, *args, **options):
        espacios = Espacio.objects.filter(estado=Espacio.ESTADO_DISPONIBLE)
        creados = 0

        for espacio in espacios:
            for dia, inicio, fin in HORARIOS_BASE:
                h_inicio = time(*[int(x) for x in inicio.split(':')])
                h_fin = time(*[int(x) for x in fin.split(':')])
                _, created = Horario.objects.get_or_create(
                    espacio=espacio,
                    dia_semana=dia,
                    hora_inicio=h_inicio,
                    defaults={'hora_fin': h_fin, 'activo': True},
                )
                if created:
                    creados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Listo. {creados} horarios nuevos creados '
                f'({espacios.count()} espacios procesados).'
            )
        )
