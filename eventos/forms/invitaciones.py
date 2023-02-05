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
    cliente = forms.CharField(widget=forms.TextInput(attrs={'class': 'cliente_search'}))

    class Meta:
        model = Invitacion
        fields = ['cliente', 'lista']

    def __init__(self, *args, **kwargs):
        super(InvitacionAssignForm, self).__init__()

    def clean_cliente(self):
        cliente = super(InvitacionAssignForm, self).clean_cliente()
        if cliente:
            cliente = cliente.split(" ").remove('')
            try:
                cliente = Persona.objects.get(nombre=cliente)
            except models.ObjectDoesNotExist:
                cliente = Persona(nombre=cliente)
                cliente.save()
        else:
            raise forms.ValidationError('Este campo no puede estar vacío.')
        return cliente

    def save(self, evento, usuario):
        instance = super(InvitacionAssignForm, self).save(commit=False)
        assert isinstance(evento, Evento), TypeError('evento should be of type Evento')
        instance.evento = evento
        instance.vendedor = usuario
        instance.estado = 'ACT'
        instance.administrador = usuario
        instance.save()
        return instance


InvitacionAssignFormset = forms.modelformset_factory(Invitacion, form=InvitacionAssignForm, extra=0)
