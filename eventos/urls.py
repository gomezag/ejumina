
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', UserPanel.as_view()),
    path('personas', ListaPersona.as_view()),
    path('e/<int:evento>/p/<int:persona>/', PanelEventoPersona.as_view()),
]
