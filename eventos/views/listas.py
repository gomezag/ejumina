"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""
from django.shortcuts import render

from eventos.forms import ListaInvitadosForm
from eventos.models import ListaInvitados
from eventos.views.basic_view import AdminView


class ListaListasInvitados(AdminView):
    template_name = 'eventos/lista_listas_invitados.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        c['listas'] = ListaInvitados.objects.all()
        return c

    def get(self, request):
        user = request.user
        c = self.get_context_data(user)
        c['form'] = ListaInvitadosForm()
        return super().get(request, c)

    def post(self, request):
        c = self.get_context_data(request.user)
        form = ListaInvitadosForm(request.POST)
        if form.is_valid():
            form.save()
        c['form'] = form
        return render(request, self.template_name, context=c)


class PanelListasInvitados(AdminView):
    template_name = 'eventos/panel-listas-invitados.html'

    def get_context_data(self, user, lista, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        c['lista'] = lista
        c['back'] = '/listas'
        return c

    def get(self, request, lista):
        lista = ListaInvitados.objects.get(slug=lista)
        c = self.get_context_data(request.user, lista)
        c['form'] = ListaInvitadosForm(instance=lista)
        return render(request, self.template_name, context=c)

    def post(self, request, lista):
        lista = ListaInvitados.objects.get(slug=lista)
        c = self.get_context_data(request.user, lista)
        form = ListaInvitadosForm(request.POST, instance=lista)
        if form.is_valid():
            form.save()
        c['form'] = form
        return render(request, self.template_name, context=c)
