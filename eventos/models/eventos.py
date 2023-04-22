"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
from django.db.models import Model
from django.db.models.fields import CharField, DateField, SlugField
from django.utils.timezone import now

from simple_history.models import HistoricalRecords

from eventos.utils import unique_slugify


ESTADOS_EVENTO = [
    ('INA', 'Inactivo'),
    ('ACT', 'Activo'),
]


class Evento(Model):
    name = CharField(max_length=100, blank=False, null=False)
    estado = CharField(max_length=3, blank=False, null=False, choices=ESTADOS_EVENTO)
    fecha = DateField(default=now)
    slug = SlugField(blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return " - ".join([self.estado, self.name, str(self.fecha)])

    def save(self, **kwargs):
        slug_str = "%s %s" % (self.name, self.fecha)
        unique_slugify(self, slug_str)
        super().save(**kwargs)
