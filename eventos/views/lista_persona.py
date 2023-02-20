"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""

from django.views import View
from django.shortcuts import render
from eventos.models import Usuario, Persona
from eventos.forms import PersonaForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from eventos.forms import InvitacionAssignFormset
from .basic_view import BasicView


@method_decorator(login_required, name='get')
class ListaPersona(BasicView):
    def get_context_data(self, user, persona=None):
        c = super(ListaPersona, self).get_context_data(user)
        c['personas'] = Persona.objects.all()
        if persona is None:
            c['form'] = PersonaForm()
        else:
            c['form'] = PersonaForm(initial=persona)
        return c

    def get(self, request, *args, **kwargs):

        user = request.user
        c = self.get_context_data(user)

        return render(request=request, template_name='eventos/lista_personas.html', context=c)

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
        return render(request, 'eventos/lista_personas.html', context=c)

