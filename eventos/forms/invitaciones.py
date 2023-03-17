"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""
from django import forms
from django.forms.widgets import Widget
from django.db.models import ObjectDoesNotExist

from eventos.models import *
from eventos.forms.validators import *
from eventos.utils import validate_in_group


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
        try:
            self.fields['lista'].initial = ListaInvitados.objects.get(nombre=usuario.username)
        except ObjectDoesNotExist:
            pass
        max_frees = Free.objects.filter(vendedor=usuario, cliente__isnull=True).count()

        self.fields['frees'].widget.attrs['max'] = max_frees

        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'input'

    def save(self, user, persona, evento, **kwargs):
        n_frees = self.cleaned_data.get('frees')
        n_invis = self.cleaned_data.get('invitaciones')
        if not user in list(self.cleaned_data.get('lista').administradores.all()):
            raise ValidationError("No podes editar esta lista.")
        if evento.estado == 'INA':
            raise ValidationError("El evento esta inactivo!")
        if persona.estado == 'INA':
            raise ValidationError("La persona esta inactiva.")
        if validate_in_group(user, ('admin',)):
            for n in range(n_frees):
                free = Free()
                free.evento = self.cleaned_data['evento']
                free.vendedor = user
                free.cliente = persona
                free.estado = 'ACT'
                free.save()
                free.administrador.set([user])
                free.save()
        else:
            free_set = Free.objects.filter(vendedor=user, evento=evento, cliente__isnull=True)
            if n_frees > 0:
                for n in range(n_frees):
                    try:
                        free = free_set[n]
                    except IndexError:
                        self.add_error('frees', 'No tenés suficientes frees! Se añadieron {}'.format(str(n)))
                        break
                    free.cliente = persona
                    free.lista = self.cleaned_data.get('lista')
                    free.estado = 'ACT'
                    free.save()

        if n_invis > 0:
            for n in range(n_invis):
                invi = Invitacion()
                invi.cliente = persona
                invi.vendedor = user
                invi.lista = self.cleaned_data.get('lista')
                invi.evento = evento
                invi.estado = 'ACT'
                invi.save()


class InvitacionAssignForm(MultiInviAssignToPersona):
    persona = forms.CharField(required=True, label="Nombre")
    cedula = forms.CharField(required=True, label="C.I.")
    invitar = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    def __init__(self, user, *args, **kwargs):
        super(InvitacionAssignForm, self).__init__(user, None, *args, **kwargs)
        self.fields['persona'].widget.attrs['class'] = 'input persona'
        self.fields['cedula'].widget.attrs['class'] = 'input cedula'

    def clean(self):
        form_data = super().clean()
        try:
            persona = Persona.objects.get(cedula=form_data['cedula'])
            if persona.nombre != form_data['persona']:
                self.add_error("persona", "Nombre no coincide con una persona existente que tiene la misma C.I.")
                raise ValidationError("Nombre no coincide con una persona existente que tiene la misma C.I.")
        except ObjectDoesNotExist:
            pass

    def clean_cedula(self):
        data = self.cleaned_data['cedula']
        return data.replace('.', '').lstrip(' ').rstrip(' ')

    def save(self, user, evento, **kwargs):
        if evento.estado == 'INA':
            raise ValidationError("El evento está inactivo!")
        nombre = self.cleaned_data['persona']
        cedula = self.cleaned_data['cedula'].replace('.', '')
        persona, created = Persona.objects.get_or_create(nombre=nombre, cedula=cedula)
        if created:
            persona.save()
        super().save(user, persona, evento, **kwargs)


InvitacionAssignFormset = forms.modelformset_factory(Invitacion, form=InvitacionAssignForm, extra=0, exclude=['id'])


class FreeAssignToUserForm(forms.Form):
    free = forms.IntegerField(min_value=0)
    evento = forms.ModelChoiceField(queryset=Evento.objects.filter(estado='ACT'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, user, vendedor):
        evento = self.cleaned_data['evento']
        if evento.estado == 'INA':
            raise ValidationError("El evento está inactivo!")
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
    file = forms.FileField(validators=[file_size], label="Archivo")
    evento = forms.ModelChoiceField(queryset=Evento.objects.filter(estado='ACT'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'file-input'


class CheckInForm(forms.Form):
    persona = forms.ModelChoiceField(queryset=Persona.objects.all(), widget=forms.HiddenInput)
    check_invis = forms.IntegerField(initial=0)
    check_frees = forms.IntegerField(initial=0)
    evento = None

    def __init__(self, *args, **kwargs):
        vendedor = kwargs.pop('vendedor', None)
        lista = kwargs.pop('lista', None)
        super().__init__(*args, **kwargs)
        if vendedor:
            self._vendedor = vendedor
        else:
            self._vendedor = None
        if lista:
            self._lista = lista
        else:
            self._lista = None

    def is_valid(self, **kwargs):
        evento = kwargs.pop('evento', None)
        extra = {}
        if self._vendedor:
            extra.update({'vendedor': self._vendedor})
        if self._lista:
            extra.update({'lista': self._lista})
        if not evento or not isinstance(evento, Evento):
            return False
        self.evento = evento
        r = super().is_valid()
        if r:
            persona = self.cleaned_data['persona']
            n_invis = self.cleaned_data['check_invis']
            n_frees = self.cleaned_data['check_frees']
            if n_invis > Invitacion.objects.filter(cliente=persona, evento=evento, estado='ACT', **extra).count() and n_invis > 0:
                self.errors.append('Demasiados check-ins para esta persona y evento.')
                return False
            elif -n_invis > Invitacion.objects.filter(cliente=persona, evento=evento, estado='USA', **extra).count() and n_invis < 0:
                self.errors.append('Demasiados check-ins para esta persona y evento.')
                return False
            if n_frees > Free.objects.filter(cliente=persona, evento=evento, estado='ACT', **extra).count():
                self.errors.append('Demasiados check-ins para esta persona y evento.')
                return False
            elif -n_frees > Free.objects.filter(cliente=persona, evento=evento, estado='USA', **extra).count() and n_frees < 0:
                self.errors.append('Demasiados check-ins para esta persona y evento.')
                return False
        return r

    def save(self):
        persona = self.cleaned_data['persona']
        evento = self.evento
        n_invis = self.cleaned_data['check_invis']
        n_frees = self.cleaned_data['check_frees']
        extra = {}
        if self._vendedor:
            extra.update({'vendedor': self._vendedor})
        if self._lista:
            extra.update({'lista': self._lista})
        if n_invis>0:
            invis = list(Invitacion.objects.filter(cliente=persona, evento=evento, estado='ACT', **extra))
            for n in range(n_invis):
                invis[n].estado = 'USA'
                invis[n].save()
        elif n_invis < 0:
            invis = list(Invitacion.objects.filter(cliente=persona, evento=evento, estado='USA', **extra))
            for n in range(-n_invis):
                invis[n].estado = 'ACT'
                invis[n].save()
        if n_frees>0:
            frees = list(Free.objects.filter(cliente=persona, evento=evento, estado='ACT', **extra))
            for n in range(n_frees):
                frees[n].estado = 'USA'
                frees[n].save()
        elif n_frees < 0:
            frees = list(Free.objects.filter(cliente=persona, evento=evento, estado='USA', **extra))
            for n in range(-n_frees):
                frees[n].estado = 'ACT'
                frees[n].save()
