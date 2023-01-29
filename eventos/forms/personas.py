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
