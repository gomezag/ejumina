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

    class Meta:
        model = Persona
        fields = ['nombre', 'cedula']

    def __init__(self, *args, **kwargs):
        super(PersonaForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].required = True
        self.fields['cedula'].required = True

    def clean(self):
        super().clean()
        self.cleaned_data['cedula'] = self.cleaned_data['cedula'].replace('.', '').lstrip(' ').rstrip(' ')


class EventoForm(forms.ModelForm):

    class Meta:
        model = Evento
        fields = ['name', 'fecha']
        labels = {'name': 'Nombre'}

    def save(self, *args, **kwargs):
        self.instance.estado = 'ACT'
        super().save(*args, **kwargs)


class EventoDeleteForm(forms.Form):
    nombre = forms.CharField()

    def is_valid(self, evento_id):
        evento = Evento.objects.get(id=evento_id)
        r = super().is_valid()
        try:
            if evento.name != self.cleaned_data['nombre']:
                self.add_error('nombre', 'Nombre no coincide.')
                return False
        except AttributeError or KeyError:
            return False
        return r
