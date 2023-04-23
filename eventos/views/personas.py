"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""

from django.shortcuts import render
from django.core.validators import integer_validator
from django.http import HttpResponseRedirect

from eventos.forms import PersonaForm, MultiInviAssignToPersona
from eventos.models import Persona, Evento, Free, Invitacion, ListaInvitados, Usuario
from .basic_view import BasicView, AdminView
from .eventos import PanelEventoPersona


class ListaPersona(AdminView):
    template_name = 'eventos/lista_personas.html'

    def get_context_data(self, user, persona=None, *args, **kwargs):
        c = super(ListaPersona, self).get_context_data(user, *args, **kwargs)
        c['personas'] = Persona.objects.all().order_by('estado')
        c['form'] = PersonaForm()
        c['edit_form'] = PersonaForm(auto_id='edit')
        return c

    def get(self, request, *args, **kwargs):

        user = request.user
        c = self.get_context_data(user)

        return render(request=request, template_name=self.template_name, context=c)

    def post(self, request, *args, **kwargs):
        c = self.get_context_data(request.user)
        if request.POST.get('deactivate', None) is not None:
            try:
                persona = Persona.objects.get(pk=request.POST['delete'])
                persona.estado = 'INA'
                persona.save()
            except Exception as e:
                pass
        elif request.POST.get('delete', None) is not None:
            try:
                persona = Persona.objects.get(pk=request.POST['delete'])
                if persona.estado == 'INA':
                    persona.delete()
                else:
                    raise ValueError('User must be deactivated')
            except Exception as e:
                c['alert_msg'] = ['El usuario tiene invitaciones activas. Es necesario borrarlas antes.']
        elif request.POST.get('reactivate', None) is not None:
            try:
                persona = Persona.objects.get(pk=request.POST['reactivate'])
                persona.estado = 'ACT'
                persona.save()
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
        c.update(self.get_context_data(request.user))
        return render(request, template_name=self.template_name, context=c)


class PanelPersona(AdminView):
    template_name = 'eventos/panel-persona.html'

    def get_context_data(self, user, persona, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        c['back'] = '/personas'
        c['persona'] = persona
        invitaciones = []
        for evento in Evento.objects.all():
            event_invis = PanelEventoPersona.parse_invitaciones(persona, evento, user)
            if event_invis:
                invitaciones.append({'name': evento.name, 'invis': event_invis})
        c['eventos_info'] = invitaciones
        c['form'] = MultiInviAssignToPersona(user, persona)
        return c

    def get(self, request, persona, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        c = self.get_context_data(request.user, persona, *args, **kwargs)

        return render(request, self.template_name, context=c)

    def post(self, request, persona, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        delete = request.POST.get('delete', None)
        c = {}
        if delete:
            try:
                integer_validator(request.POST['lista'])
                integer_validator(request.POST['rrpp'])
                integer_validator(request.POST['evento'])
                lista = ListaInvitados.objects.get(pk=request.POST['lista'])
                rrpp = Usuario.objects.get(pk=request.POST['rrpp'])
                evento = Evento.objects.get(pk=request.POST['evento'])
            except Exception as e:
                return HttpResponseRedirect('')
            invitaciones = Invitacion.objects.filter(cliente=persona, vendedor=rrpp,
                                                     lista=lista, evento=evento)
            frees = Free.objects.filter(cliente=persona, vendedor=rrpp,
                                        lista=lista, evento=evento)

            for free in frees:
                if free.estado == 'ACT':
                    if free.vendedor.groups.filter(name='admin').exists():
                        free.delete()
                    else:
                        free.cliente = None
                        free.save()
                else:
                    c['alert_msg'] = ['No se puede borrar una entrada usada!']
            for invi in invitaciones:
                if invi.estado == 'ACT':
                    invi.delete()
                else:
                    c['alert_msg'] = ['No se puede borrar una entrada usada!']

        c.update(self.get_context_data(request.user, persona))
        return render(request, self.template_name, context=c)

