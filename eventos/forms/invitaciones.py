"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
from django import forms
from django.forms.widgets import Widget

from eventos.models import *
from eventos.forms.validators import *


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
        fields = ['nombre', 'administradores', 'color']


class MultiInviAssignToPersona(forms.Form):
    invitaciones = forms.IntegerField(min_value=0, initial=0)
    frees = forms.IntegerField(min_value=0, initial=0)
    lista = forms.ModelChoiceField(queryset=None)

    def __init__(self, usuario, persona, *args, **kwargs):
        super(MultiInviAssignToPersona, self).__init__(*args, **kwargs)
        self.fields['lista'].queryset = ListaInvitados.objects.filter(administradores__in=[usuario])

        max_frees = Free.objects.filter(vendedor=usuario, cliente__isnull=True).count()

        self.fields['frees'].widget.attrs['max'] = max_frees

        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'input'

    def save(self, user, persona, evento):
        n_frees = self.cleaned_data.get('frees')
        n_invis = self.cleaned_data.get('invitaciones')
        free_set = Free.objects.filter(vendedor=user, evento=evento, cliente__isnull=True)
        assert user in list(self.cleaned_data.get('lista').administradores.all())
        if n_frees > 0:
            for n in range(n_frees):
                try:
                    free = free_set[n]
                except IndexError:
                    self.add_error('frees', 'No tenés suficientes frees!')
                    break
                free.cliente = persona
                free.lista = self.cleaned_data.get('lista')
                free.estado = 'ACT'
                free.save()

        if n_invis>0:
            for n in range(n_invis):
                invi = Invitacion()
                invi.cliente = persona
                invi.vendedor = user
                invi.lista = self.cleaned_data.get('lista')
                invi.evento = evento
                invi.estado = 'ACT'
                invi.save()


class InvitacionAssignForm(MultiInviAssignToPersona):
    persona = forms.CharField()
    invitar = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    def __init__(self, user, *args, **kwargs):
        super(InvitacionAssignForm, self).__init__(user, None, *args, **kwargs)
        self.fields['persona'].widget.attrs['class'] = 'input persona'

    def save(self, user, evento):
        nombre = self.cleaned_data['persona']
        persona, created = Persona.objects.get_or_create(nombre=nombre)
        if created:
            persona.save()
        super().save(user, persona, evento)


InvitacionAssignFormset = forms.modelformset_factory(Invitacion, form=InvitacionAssignForm, extra=0, exclude=['id'])


class FreeAssignToUserForm(forms.Form):
    free = forms.IntegerField(min_value=0)
    evento = forms.ModelChoiceField(queryset=Evento.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, user, vendedor):
        for n in range(self.cleaned_data['free']):
            free = Free()
            free.evento = self.cleaned_data['evento']
            free.vendedor = vendedor
            free.cliente = None
            free.estado = 'ACT'
            free.save()
            free.administrador.set([user])
            free.save()


class ExcelImportForm(forms.Form):
    file = forms.FileField(validators=[file_size])
    evento = forms.ModelChoiceField(queryset=Evento.objects.all())


class CheckInForm(forms.Form):
    evento = forms.ModelChoiceField(queryset=Evento.objects.all())
    persona = forms.ModelChoiceField(queryset=Persona.objects.all())
    check_invis = forms.IntegerField()
    check_frees = forms.IntegerField()

    def is_valid(self, **kwargs):
        r = super().is_valid()
        if r:
            persona = self.cleaned_data['persona']
            evento = self.cleaned_data['evento']
            n_invis = self.cleaned_data['check_invis']
            n_frees = self.cleaned_data['check_frees']
            if n_invis > Invitacion.objects.filter(cliente=persona, evento=evento, estado='ACT').count():
                self.errors.append('Demasiados check-ins para esta persona y evento.')
                return False
            if n_frees > Free.objects.filter(cliente=persona, evento=evento, estado='ACT').count():
                self.errors.append('Demasiados check-ins para esta persona y evento.')
                return False
        return r

    def save(self):
        persona = self.cleaned_data['persona']
        evento = self.cleaned_data['evento']
        n_invis = self.cleaned_data['check_invis']
        n_frees = self.cleaned_data['check_frees']
        invis = list(Invitacion.objects.filter(cliente=persona, evento=evento, estado='ACT'))
        frees = list(Free.objects.filter(cliente=persona, evento=evento, estado='ACT'))
        for n in range(n_invis):
            invis[n].estado = 'USA'
            invis[n].save()
        for n in range(n_frees):
            frees[n].estado = 'USA'
            frees[n].save()
