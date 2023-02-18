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
from eventos.forms import PersonaForm, ListaInvitadosForm, InvitacionAssignForm
from django.db.models.base import ObjectDoesNotExist
from eventos.utils import read_client_list


@method_decorator(login_required, name='get')
class PanelEvento(View):

    def get_context_data(self, user, evento=None, persona=None):
        c = dict()
        c['usuario'] = user.nombre
        if evento and not isinstance(evento, Evento):
            c['evento'] = Evento.objects.get(id=evento)
        else:
            c['evento'] = Evento.objects.all()[0]

        c['invi_dadas'] = c['evento'].invitacion_set.filter(cliente=None, vendedor=user)
        return c

    def get(self, request, evento, *args, **kwargs):
        user = Usuario.objects.get(user=request.user)
        if user is None:
            return GenericViewError('User is None')
        # Check query
        persona = request.GET.get('persona', None)
        c = self.get_context_data(user, evento, persona)
        c['persona_form'] = PersonaForm(evento)
        c['lista_form'] = InvitacionAssignForm(usuario=Usuario.objects.get(user=request.user))
        print(c['evento'].invitacion_set.all())
        c['invi_totales'] = len(c['evento'].invitacion_set.all())
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
        return render(request, 'eventos/panel_usuario.html', context=c)

    def post(self, request, evento, *args, **kwargs):

        form = InvitacionAssignForm(request.POST, usuario=Usuario.objects.get(user=request.user))
        evento = Evento.objects.get(id=evento)
        usuario = Usuario.objects.get(user=request.user)
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
