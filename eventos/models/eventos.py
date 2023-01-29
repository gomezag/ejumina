from django.db.models import Model
from django.db.models.fields import CharField


ESTADOS_EVENTO = [
    ('NOP', 'No Publicado'),
    ('PUB', 'Publicado'),
    ('ONG', 'Puertas Abiertas'),
    ('DON', 'Realizado'),
    ('CAN', 'Cancelado'),
]


class Evento(Model):
    name = CharField(max_length=100, blank=False, null=False)
    estado = CharField(max_length=3, blank=False, null=False, choices=ESTADOS_EVENTO)

    def __str__(self):
        return " - ".join([self.estado, self.name])
