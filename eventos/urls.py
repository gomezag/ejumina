"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""

from django.urls import path
from .views import *

urlpatterns = [
    path('e/<int:evento>', PanelEvento.as_view()),
    path('personas', ListaPersona.as_view()),
    path('usuarios', ListaUsuarios.as_view()),
    path('e/<int:evento>/p/<int:persona>/', PanelEventoPersona.as_view()),
    path('u/<int:id_usuario>', PanelUsuario.as_view()),
    path('', ListaEventos.as_view()),
    path('listas', ListaListasInvitados.as_view()),
    path('importar', ImportView.as_view())
]
