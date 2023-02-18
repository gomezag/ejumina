"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
from django import forms
from django.db import models
from ..models import *
from django.forms.widgets import Widget


class DisplayOnlyField(Widget):

    def __init__(self, attrs=None):
        self.attrs = attrs or {}
        self.required = False

    def render(self, name, value, attrs=None, **kwargs):
        try:
            val = value
        except AttributeError:
            val = ""
        return val


class ListaInvitadosForm(forms.ModelForm):

    class Meta:
        model = ListaInvitados
        fields = '__all__'


class InvitacionAssignForm(forms.ModelForm):
    persona = forms.CharField()

    class Meta:
        model = Invitacion
        fields = ['persona', 'lista']

    def __init__(self, *args, **kwargs):
        super(InvitacionAssignForm, self).__init__(*args, **kwargs)
        self.fields['persona'].widget.attrs['class'] = 'input'


    def __init__(self, *args, **kwargs):
        queryset = ListaInvitados.objects.filter(administradores__in=[kwargs.pop('usuario')])
        super(InvitacionAssignForm, self).__init__(*args, **kwargs)
        self.fields['lista'].queryset = queryset

    def save(self, evento, usuario):
        cliente_name = self.cleaned_data['persona'].split(" ")
        try:
            cliente_name.remove('')
        except ValueError:
            pass
        cliente_name = ' '.join(cliente_name)
        cliente, created = Persona.objects.get_or_create(
            nombre=cliente_name
        )
        instance = super(InvitacionAssignForm, self).save(commit=False)
        assert isinstance(evento, Evento), TypeError('evento should be of type Evento')
        instance.evento = evento
        instance.vendedor = usuario
        instance.estado = 'ACT'
        instance.cliente = cliente
        instance.save()
        instance.administrador.add(usuario)
        return instance


InvitacionAssignFormset = forms.modelformset_factory(Invitacion, form=InvitacionAssignForm, extra=0)
