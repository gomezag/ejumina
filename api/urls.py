"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""

from django.urls import path
from .views import *

urlpatterns = [
    path('search/persona/', Personas.as_view())
]
