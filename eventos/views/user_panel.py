from django.views import View
from django.views.generic import GenericViewError
from django.shortcuts import render
from eventos.models import Usuario, Evento, Persona
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from eventos.forms import PersonaForm, ListaInvitadosForm
from django.db.models.base import ObjectDoesNotExist

@method_decorator(login_required, name='get')
class UserPanel(View):

    def get_context_data(self, user, evento=None, persona=None):
        c = dict()
        c['usuario'] = user.nombre
        if evento:
            c['evento'] = Evento.objects.get(pk=evento)
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
        evento = request.GET.get('evento')
        try:
            evento = Evento.objects.get(pk=evento)
        except ObjectDoesNotExist:
            evento = None
        persona = request.GET.get('persona', None)
        c = self.get_context_data(user, evento, persona)
        c['persona_form'] = PersonaForm(evento)
        c['lista_form'] = ListaInvitadosForm()
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
