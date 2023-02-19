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
from eventos.models import Usuario, Evento, Persona, ListaInvitados, Invitacion
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from eventos.forms import PersonaForm, ListaInvitadosForm, InvitacionAssignForm, MultiInviAssignToPersona
from django.db.models.base import ObjectDoesNotExist
from eventos.utils import read_client_list
from .basic_view import BasicView


@method_decorator(login_required, name='get')
class PanelEvento(BasicView):

    def get_context_data(self, user, evento=None, persona=None, *args, **kwargs):
        c = super(PanelEvento, self).get_context_data(user, *args, **kwargs)
        if evento and not isinstance(evento, Evento):
            c['evento'] = Evento.objects.get(id=evento)
        else:
            c['evento'] = Evento.objects.all()[0]
        c['personas'] = []
        for persona in Persona.objects.all():
            try:
                invitaciones = Invitacion.objects.filter(evento=c['evento'], cliente=persona)
                listas = ListaInvitados.objects.filter(personas=persona).distinct()
            except ObjectDoesNotExist:
                invitaciones = listas = []

            c['personas'].append({'nombre': persona.nombre,
                                  'pk': persona.pk,
                                  'invitaciones': len(invitaciones),
                                  'listas': list(listas)})
        c['invi_dadas'] = c['evento'].invitacion_set.filter(vendedor=c['usuario']).exclude(cliente=None)
        c['free_dados'] = c['evento'].free_set.filter(vendedor=c['usuario']).exclude(cliente=None)
        return c

    def get(self, request, evento, *args, **kwargs):
        user = request.user
        # Check query
        persona = request.GET.get('persona', None)
        c = self.get_context_data(user, evento, persona)
        c['persona_form'] = InvitacionAssignForm(usuario=c['usuario'])
        c['invi_totales'] = len(c['evento'].invitacion_set.all())

        return render(request, 'eventos/panel_usuario.html', context=c)

    def post(self, request, evento, *args, **kwargs):

        evento = Evento.objects.get(id=evento)
        user = request.user
        c = self.get_context_data(user, evento, None)
        form = InvitacionAssignForm(request.POST, usuario=c['usuario'])

        if form.is_valid():
            form.save(evento, c['usuario'])

        c['persona_form'] = PersonaForm(evento)
        c['lista_form'] = form
        return render(request, 'eventos/panel_usuario.html', context=c)


class PanelEventoPersona(BasicView):
    def get_context_data(self, user, persona, evento, *args, **kwargs):
        c = super(PanelEventoPersona, self).get_context_data(user, *args, **kwargs)
        invitaciones = persona.invitacion_set.filter(evento=evento)
        c['persona'] = persona
        c['evento'] = evento
        c['invitaciones'] = invitaciones
        return c

    def get(self, request, persona, evento, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        evento = Evento.objects.get(pk=evento)
        c = self.get_context_data(request.user, persona, evento)
        usuario = Usuario.objects.get(user=request.user)
        c['form'] = MultiInviAssignToPersona(usuario)
        return render(request, 'eventos/persona_view_evento.html', context=c)


class ListaUsuarios(View):


    def get(self, request, *args, **kwargs):
        pass


class ListaEventos(BasicView):

    def get(self, request):
        user = request.user
        c = self.get_context_data(user)
        c['eventos'] = Evento.objects.all()

        return render(request, 'eventos/lista_eventos.html', context=c)