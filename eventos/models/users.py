"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
from django.contrib.auth.models import User, AbstractBaseUser, AbstractUser
from django.db.models import OneToOneField, ManyToManyField, ForeignKey
from django.db.models import Model, CASCADE, SET_NULL
from django.db.models.fields import IntegerField, CharField
from django.db.models.signals import pre_save
from django.dispatch import receiver

ESTADOS_CLIENTES = [
    ('ACT', 'Activo'),
    ('BAN', 'Baneado'),
    ('INA', 'Inactivo'),
]


class Persona(Model):
    nombre = CharField(max_length=100, blank=False, null=False)
    estado = CharField(max_length=3, blank=False, null=False, choices=ESTADOS_CLIENTES, default='ACT')

    def __str__(self):
        return " - ".join([str(self.nombre), str(self.estado)])


class Usuario(AbstractUser):
    ROLES_USUARIO = [
        (0, 'Admin'),
        (1, 'Bouncer'),
        (2, 'R.R.P.P.'),
        (3, 'Guest')
    ]
    rol = IntegerField(choices=ROLES_USUARIO)

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"


@receiver(pre_save, sender=Usuario, dispatch_uid="user_count")
def crear_usuario(sender, instance, **kwargs):
    if not instance.rol:
        instance.rol = 3
