"""
Comando para cargar datos de prueba de Espacios y Horarios.
Uso: python manage.py seed_espacios
"""

from django.core.management.base import BaseCommand
from espacios.models import Espacio, Horario


ESPACIOS_DATA = [
    {
        'nombre': 'Aula 101',
        'tipo': 'aula',
        'capacidad': 30,
        'ubicacion': 'Bloque A, Piso 1',
        'estado': 'disponible',
        'descripcion': 'Aula estándar con proyector y pizarrón.',
        'equipamiento': 'Proyector, pizarrón, 30 sillas, aire acondicionado',
    },
    {
        'nombre': 'Aula 202',
        'tipo': 'aula',
        'capacidad': 40,
        'ubicacion': 'Bloque A, Piso 2',
        'estado': 'disponible',
        'descripcion': 'Aula amplia para grupos grandes.',
        'equipamiento': 'Proyector, pizarrón, 40 sillas',
    },
    {
        'nombre': 'Laboratorio de Sistemas',
        'tipo': 'laboratorio',
        'capacidad': 25,
        'ubicacion': 'Bloque B, Piso 1',
        'estado': 'disponible',
        'descripcion': 'Laboratorio con 25 computadores.',
        'equipamiento': '25 PCs, proyector, aire acondicionado',
    },
    {
        'nombre': 'Laboratorio de Redes',
        'tipo': 'laboratorio',
        'capacidad': 20,
        'ubicacion': 'Bloque B, Piso 2',
        'estado': 'disponible',
        'descripcion': 'Laboratorio especializado en redes.',
        'equipamiento': '20 PCs, equipos de red, proyector',
    },
    {
        'nombre': 'Sala de Reuniones A',
        'tipo': 'sala',
        'capacidad': 10,
        'ubicacion': 'Bloque C, Piso 1',
        'estado': 'disponible',
        'descripcion': 'Sala para reuniones pequeñas.',
        'equipamiento': 'TV 55", mesa redonda, 10 sillas',
    },
    {
        'nombre': 'Auditorio Principal',
        'tipo': 'auditorio',
        'capacidad': 200,
        'ubicacion': 'Edificio Central',
        'estado': 'disponible',
        'descripcion': 'Auditorio para eventos institucionales.',
        'equipamiento': 'Sistema de sonido, proyector, 200 sillas, escenario',
    },
    {
        'nombre': 'Sala de Cómputo',
        'tipo': 'laboratorio',
        'capacidad': 15,
        'ubicacion': 'Bloque D, Piso 1',
        'estado': 'mantenimiento',
        'descripcion': 'En mantenimiento por actualización de equipos.',
        'equipamiento': '15 PCs',
    },
]

# Horarios: (dia_semana, hora_inicio, hora_fin)
HORARIOS_BASE = [
    (0, '07:00', '09:00'),
    (0, '09:00', '11:00'),
    (0, '11:00', '13:00'),
    (0, '14:00', '16:00'),
    (0, '16:00', '18:00'),
    (1, '07:00', '09:00'),
    (1, '09:00', '11:00'),
    (1, '14:00', '16:00'),
    (2, '07:00', '09:00'),
    (2, '11:00', '13:00'),
    (2, '16:00', '18:00'),
    (3, '09:00', '11:00'),
    (3, '14:00', '16:00'),
    (4, '07:00', '09:00'),
    (4, '09:00', '11:00'),
    (4, '14:00', '16:00'),
]


class Command(BaseCommand):
    help = 'Carga datos de prueba para Espacios y Horarios'

    def handle(self, *args, **options):
        self.stdout.write('Cargando datos de prueba...')

        creados = 0
        for data in ESPACIOS_DATA:
            espacio, created = Espacio.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data,
            )
            if created:
                creados += 1
                self.stdout.write(f'  ✓ Espacio creado: {espacio.nombre}')

                # Solo agregar horarios a espacios disponibles
                if espacio.estado == 'disponible':
                    for dia, inicio, fin in HORARIOS_BASE[:8]:  # 8 horarios por espacio
                        try:
                            from datetime import time
                            h_inicio = time(*[int(x) for x in inicio.split(':')])
                            h_fin = time(*[int(x) for x in fin.split(':')])
                            Horario.objects.get_or_create(
                                espacio=espacio,
                                dia_semana=dia,
                                hora_inicio=h_inicio,
                                defaults={'hora_fin': h_fin, 'activo': True},
                            )
                        except Exception:
                            pass
            else:
                self.stdout.write(f'  — Ya existe: {espacio.nombre}')

        self.stdout.write(
            self.style.SUCCESS(f'\nListo. {creados} espacios nuevos creados.')
        )
