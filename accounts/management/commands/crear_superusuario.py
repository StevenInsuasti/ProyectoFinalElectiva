"""
Comando para crear el superusuario administrador inicial.
Se ejecuta en el buildCommand de Render para inicializar la BD.

Uso:
    python manage.py crear_superusuario

Lee las credenciales desde variables de entorno:
    DJANGO_SUPERUSER_USERNAME  (default: admin)
    DJANGO_SUPERUSER_EMAIL     (default: admin@reservas.com)
    DJANGO_SUPERUSER_PASSWORD  (default: Admin1234!)
"""

import os
from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Crea el superusuario administrador inicial si no existe'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@reservas.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin1234!')

        if CustomUser.objects.filter(username=username).exists():
            # Si ya existe, actualizar la contraseña con la del entorno
            user = CustomUser.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Contraseña del superusuario "{username}" actualizada.')
            )
            return

        CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            rol=CustomUser.ROL_ADMINISTRADOR,
            first_name='Admin',
            last_name='Sistema',
        )
        self.stdout.write(
            self.style.SUCCESS(f'Superusuario "{username}" creado exitosamente.')
        )
