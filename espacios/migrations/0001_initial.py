"""
Migración inicial para los modelos Espacio y Horario.
Generada manualmente - Integrante 2
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Espacio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre')),
                ('tipo', models.CharField(
                    choices=[
                        ('aula', 'Aula'),
                        ('laboratorio', 'Laboratorio'),
                        ('sala', 'Sala de Reuniones'),
                        ('auditorio', 'Auditorio'),
                        ('otro', 'Otro'),
                    ],
                    default='aula',
                    max_length=20,
                    verbose_name='Tipo',
                )),
                ('capacidad', models.PositiveIntegerField(verbose_name='Capacidad (personas)')),
                ('ubicacion', models.CharField(max_length=200, verbose_name='Ubicación')),
                ('estado', models.CharField(
                    choices=[
                        ('disponible', 'Disponible'),
                        ('mantenimiento', 'En Mantenimiento'),
                        ('inactivo', 'Inactivo'),
                    ],
                    default='disponible',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('equipamiento', models.TextField(
                    blank=True,
                    help_text='Ej: proyector, aire acondicionado, pizarrón',
                    null=True,
                    verbose_name='Equipamiento',
                )),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Última actualización')),
            ],
            options={
                'verbose_name': 'Espacio',
                'verbose_name_plural': 'Espacios',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.IntegerField(
                    choices=[
                        (0, 'Lunes'),
                        (1, 'Martes'),
                        (2, 'Miércoles'),
                        (3, 'Jueves'),
                        (4, 'Viernes'),
                        (5, 'Sábado'),
                        (6, 'Domingo'),
                    ],
                    verbose_name='Día de la semana',
                )),
                ('hora_inicio', models.TimeField(verbose_name='Hora de inicio')),
                ('hora_fin', models.TimeField(verbose_name='Hora de fin')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('espacio', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='horarios',
                    to='espacios.espacio',
                    verbose_name='Espacio',
                )),
            ],
            options={
                'verbose_name': 'Horario',
                'verbose_name_plural': 'Horarios',
                'ordering': ['espacio', 'dia_semana', 'hora_inicio'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='horario',
            unique_together={('espacio', 'dia_semana', 'hora_inicio')},
        ),
    ]
