"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
from django import forms
from django.db import models
from eventos.models import *
from django.forms.widgets import Widget


class PersonaForm(forms.ModelForm):

    listas = forms.ModelMultipleChoiceField(
        queryset=ListaInvitados.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Persona
        fields = ['nombre', 'listas']

    def __init__(self, evento, *args, **kwargs):
        super(PersonaForm, self).__init__(*args, **kwargs)
