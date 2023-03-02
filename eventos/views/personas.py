"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""

import itertools

from django.shortcuts import render
from django.db.models import Count

from eventos.forms import *
from .basic_view import BasicView
from .eventos import PanelEventoPersona


class ListaPersona(BasicView):
    template_name = 'eventos/lista_personas.html'

    def get_context_data(self, user, persona=None, *args, **kwargs):
        c = super(ListaPersona, self).get_context_data(user, *args, **kwargs)
        c['personas'] = Persona.objects.all()
        c['form'] = PersonaForm()
        c['edit_form'] = PersonaForm(auto_id='edit')
        return c

    def get(self, request, *args, **kwargs):

        user = request.user
        c = self.get_context_data(user)

        return render(request=request, template_name=self.template_name, context=c)

    def post(self, request, *args, **kwargs):
        if request.POST.get('delete', None) is not None:
            try:
                persona = Persona.objects.get(pk=request.POST['delete'])
                persona.delete()
            except Exception as e:
                pass
        elif request.POST.get('edit', None) is not None:
            try:
                persona = Persona.objects.get(pk=request.POST['edit'])
                form = PersonaForm(request.POST, instance=persona)
                if form.is_valid():
                    form.save()
            except Exception as e:
                print(repr(e))
                pass
        else:
            form = PersonaForm(data=request.POST)
            if form.is_valid():
                form.save()
        c = self.get_context_data(request.user)
        return render(request, template_name=self.template_name, context=c)


class PanelPersona(BasicView):
    template_name = 'eventos/panel-persona.html'

    def get_context_data(self, user, persona, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        c['back'] = '/personas'
        c['persona'] = persona
        invitaciones = []
        for evento in Evento.objects.all():
            event_invis = PanelEventoPersona.parse_invitaciones(persona, evento)
            if event_invis:
                invitaciones.append({'name': evento.name, 'invis': event_invis})
        c['eventos_info'] = invitaciones
        return c

    def get(self, request, persona, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        c = self.get_context_data(request.user, persona, *args, **kwargs)

        return render(request, self.template_name, context=c)