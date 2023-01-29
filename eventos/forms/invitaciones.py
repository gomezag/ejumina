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

    evento = models.ForeignKey('Evento', models.DO_NOTHING, db_column='name')

    class Meta:
        model = Invitacion
        fields = ['cliente']

    def __init__(self, *args, **kwargs):
        super(InvitacionAssignForm, self).__init__()
        self.fields['cliente'].widget = forms.TextInput(attrs={'class': 'cliente_search'})

    def save(self, evento, usuario):
        instance = super(InvitacionAssignForm, self).save(commit=False)
        assert isinstance(evento, Evento), TypeError('evento should be of type Evento')
        instance.evento = evento
        instance.save()
        return instance


InvitacionAssignFormset = forms.modelformset_factory(Invitacion, form=InvitacionAssignForm, extra=0)
