"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""
from django.views import View
from django.views.generic import GenericViewError
from django.shortcuts import render
from eventos.models import Usuario, Evento, Persona
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from eventos.forms import PersonaForm, ListaInvitadosForm, InvitacionAssignForm
from django.db.models.base import ObjectDoesNotExist
from eventos.utils import read_client_list


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class UserPanel(View):

    def get_evento(self, rget):
        evento = rget.get('evento')
        try:
            evento = Evento.objects.get(pk=evento)
        except ObjectDoesNotExist:
            evento = Evento.objects.all()[0]
        return evento

    def get_context_data(self, user, evento=None, persona=None):
        c = dict()
        c['usuario'] = user.nombre
        if evento:
            c['evento'] = evento
        else:
            c['evento'] = Evento.objects.all()[0]
        if persona is None:
            c['personas'] = Persona.objects.all().order_by('nombre')
        else:
            c['personas'] = Persona.objects.filter(nombre__icontains=persona)

        c['invi_dadas'] = c['evento'].invitacion_set.filter(cliente=None)
        return c

    def get(self, request, *args, **kwargs):
        user = Usuario.objects.get(user=request.user)
        if user is None:
            return GenericViewError('User is None')
        # Check query
        evento = self.get_evento(request.GET)
        persona = request.GET.get('persona', None)
        c = self.get_context_data(user, evento, persona)
        c['persona_form'] = PersonaForm(evento)
        c['lista_form'] = InvitacionAssignForm()

        return render(request, 'eventos/panel_usuario.html', context=c)

    def post(self, request, *args, **kwargs):

        form = InvitacionAssignForm(request.POST)
        evento = self.get_evento(request.POST)
        usuario = Usuario.objects.get(user=request.user)

        form.instance.evento = evento
        form.instance.vendedor = usuario
        form.instance.administrador = usuario
        print(form.is_valid())
        print(form.__dict__)
        print(form.errors.renderer)
        if form.is_valid():
            form.save(evento, usuario)
        # if kwargs.get('import', None):
        #     file = request.FILES['file']
        #     file_data = file.read()
        #     df = read_client_list(file_data)
        c = self.get_context_data(usuario, evento, None)
        c['persona_form'] = PersonaForm(evento)
        c['lista_form'] = form
        return render(request, 'eventos/panel_usuario.html', context=c)


class PanelEventoPersona(View):
    def get_context_data(self, user, persona, evento):
        invitaciones = persona.invitacion_set.filter(evento=evento)
        c = {}
        c['usuario'] = Usuario.objects.get(user=user).nombre
        c['persona'] = persona
        c['evento'] = evento
        c['invitaciones'] = invitaciones

        return c

    def get(self, request, persona, evento, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        evento = Evento.objects.get(pk=evento)
        c = self.get_context_data(request.user, persona, evento)

        return render(request, 'eventos/paneleventopersona.html', context=c)
