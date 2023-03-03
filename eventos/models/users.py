"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
from django.contrib.auth.models import AbstractUser, Group
from django.db.models import Model, CASCADE, SET_NULL
from django.db.models.fields import IntegerField, CharField
from django.db.models.signals import post_save
from django.dispatch import receiver

ESTADOS_CLIENTES = [
    ('ACT', 'Activo'),
    ('BAN', 'Baneado'),
    ('INA', 'Inactivo'),
]


class Persona(Model):
    nombre = CharField(max_length=100, blank=False, null=False)
    estado = CharField(max_length=3, blank=False, null=False, choices=ESTADOS_CLIENTES, default='ACT')
    cedula = CharField(max_length=11, blank=False, null=True, unique=True)

    def __str__(self):
        return " - ".join([str(self.nombre), str(self.estado)])


class Usuario(AbstractUser):
    ROLES_USUARIO = [
        (0, 'Admin'),
        (1, 'Bouncer'),
        (2, 'R.R.P.P.'),
        (3, 'Guest')
    ]
    rol = IntegerField(choices=ROLES_USUARIO, null=True, blank=True)
    first_name = CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"


@receiver(post_save, sender=Usuario, dispatch_uid="asignar_roles")
def asignar_roles(sender, instance, **kwargs):
    if not instance.rol:
        if Group.objects.get_or_create(name='admin')[0] in instance.groups.all():
            instance.rol = 0
        elif Group.objects.get_or_create(name='rrpp')[0] in instance.groups.all():
            instance.rol = 2
        elif Group.objects.get_or_create(name='entrada')[0] in instance.groups.all():
            instance.rol = 1
        else:
            instance.rol = 3
        instance.save()