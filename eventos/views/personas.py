"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""

from django.shortcuts import render
from eventos.forms import *
from .basic_view import BasicView
from django.db.models import Count
import itertools


class ListaPersona(BasicView):
    template_name = 'eventos/lista_personas.html'

    def get_context_data(self, user, persona=None, *args, **kwargs):
        c = super(ListaPersona, self).get_context_data(user, *args, **kwargs)
        c['personas'] = Persona.objects.all()
        if persona is None:
            c['form'] = PersonaForm()
        else:
            c['form'] = PersonaForm(initial=persona)
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
            event_invis = []
            invis = Invitacion.objects.filter(cliente=persona, evento=evento).values('vendedor', 'lista').annotate(
                invis=Count('lista'))
            frees = Free.objects.filter(cliente=persona, evento=evento).values('vendedor', 'lista').annotate(
                frees=Count('lista'))
            all_invis = sorted(list(itertools.chain(invis, frees)), key=lambda x: (x['vendedor'], x['lista']))
            for common, all_invis_group in itertools.groupby(all_invis, key=lambda x: (x['vendedor'], x['lista'])):
                vendedor = Usuario.objects.get(pk=common[0])
                lista = ListaInvitados.objects.get(pk=common[1])
                r = {
                    'rrpp': vendedor.first_name,
                    'lista_id': lista.pk,
                    'invis': 0,
                    'frees': 0,
                }
                [r.update(i) for i in all_invis_group]
                r.update({'lista': lista.nombre})
                event_invis.append(r)
            if event_invis:
                invitaciones.append({'name': evento.name, 'invis': event_invis})
        c['eventos_info'] = invitaciones
        return c

    def get(self, request, persona, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        c = self.get_context_data(request.user, persona, *args, **kwargs)

        return render(request, self.template_name, context=c)