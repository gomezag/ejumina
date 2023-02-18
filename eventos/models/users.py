"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
from django.contrib.auth.models import User
from django.db.models import OneToOneField, ManyToManyField, ForeignKey
from django.db.models import Model, CASCADE, SET_NULL
from django.db.models.fields import IntegerField, CharField


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


class Usuario(Model):
    ROLES_USUARIO = [
        (0, 'Admin'),
        (1, 'Bouncer'),
        (2, 'R.R.P.P.'),
    ]
    user = OneToOneField(User, on_delete=CASCADE)
    rol = IntegerField(choices=ROLES_USUARIO)
    nombre = CharField(max_length=30, unique=True)
    persona = ForeignKey(Persona, null=True, blank=False, on_delete=SET_NULL)

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"


class Grupo(Model):
    miembros = ManyToManyField(Persona, blank=True)
    nombre = CharField(max_length=8, null=False, blank=False)

    def __str__(self):
        return f"{self.nombre}"