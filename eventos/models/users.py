"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
from django.contrib.auth.models import AbstractUser, Group
from django.db.models import Model, CASCADE, SET_NULL
from django.db.models.fields import IntegerField, CharField
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Persona(Model):
    ESTADOS_CLIENTES = [
        ('ACT', 'Activo'),
        ('BAN', 'Baneado'),
        ('INA', 'Inactivo'),
    ]

    nombre = CharField(max_length=100, blank=False, null=False)
    estado = CharField(max_length=3, blank=False, null=False, choices=ESTADOS_CLIENTES, default='ACT')
    cedula = CharField(max_length=11, blank=False, null=True, unique=True)

    def __str__(self):
        return " - ".join([str(self.nombre), str(self.estado)])


class Usuario(AbstractUser):
    first_name = CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.username}"


if not hasattr(Group, 'parent'):
    field = CharField(max_length=10)
    field.contribute_to_class(Group, 'label')

