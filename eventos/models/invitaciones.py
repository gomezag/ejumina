"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
import django.db.models as models
from django.db.models import ForeignKey, ManyToManyField, ObjectDoesNotExist
from django.db.models.fields import CharField, SlugField
from django.db.models.signals import post_save
from django.dispatch import receiver

from .eventos import Evento
from .users import Usuario, Persona
from eventos.utils import unique_slugify

COLORES = [
    ('#008744', 'Green'),
    ('#0057e7', 'Blue'),
    ('#d62d20', 'Red'),
    ('#ffa700', 'Yellow'),
]


ESTADOS_INVITACION = [
    ('ACT', 'Activa'),
    ('RES', 'Reservada'),
    ('USA', 'Usada'),
    ('CAN', 'Cancelada'),
]


class ListaInvitados(models.Model):
    color = CharField(max_length=9, choices=COLORES, null=False, default='#0057e7')
    personas = ManyToManyField(Persona, blank=True, through='Invitacion', related_name='invitados')
    personas_free = ManyToManyField(Persona, blank=True, through='Free', related_name='invitados_free')
    administradores = ManyToManyField(Usuario, blank=True)
    nombre = CharField(max_length=25, null=False, blank=False, unique=True)
    slug = SlugField(blank=True)

    def __str__(self):
        return self.nombre

    def save(self, **kwargs):
        slug_str = "%s" % (self.nombre)
        unique_slugify(self, slug_str)
        super().save(**kwargs)


class Invitacion(models.Model):
    estado = CharField(max_length=3, choices=ESTADOS_INVITACION, default='ACT')
    evento = ForeignKey(Evento, on_delete=models.CASCADE, null=False)
    vendedor = ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=False)
    cliente = ForeignKey(Persona, on_delete=models.PROTECT, null=True, blank=True)
    lista = ForeignKey(ListaInvitados, null=False, on_delete=models.PROTECT, blank=False)

    def __str__(self):
        return f"Invitacion a {self.evento.name} - {self.get_estado_display()} - {self.vendedor.first_name} a" \
               f" {self.cliente.nombre}"


class Free(models.Model):
    administrador = ManyToManyField(Usuario, blank=False, related_name='frees')
    estado = CharField(max_length=3, choices=ESTADOS_INVITACION, null=False)
    evento = ForeignKey(Evento, on_delete=models.CASCADE, null=False)
    vendedor = ForeignKey(Usuario, on_delete=models.PROTECT, null=False, blank=False)
    cliente = ForeignKey(Persona, on_delete=models.PROTECT, null=True, blank=True)
    lista = ForeignKey(ListaInvitados, null=True, on_delete=models.PROTECT, blank=True)

    def __str__(self):
        return f"Free a {str(self.evento.name)} - {self.get_estado_display()} - {self.vendedor.first_name} " \
               f"a {self.cliente}"


@receiver(post_save, sender=Usuario, dispatch_uid="crear_lista")
def asignar_roles(sender, instance, **kwargs):
    try:
        ListaInvitados.objects.get(nombre=instance.first_name)

    except ObjectDoesNotExist:
        lista = ListaInvitados()
        lista.nombre = instance.first_name
        lista.color = '#008744'
        lista.save()
        lista.administradores.add(instance)

