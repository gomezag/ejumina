"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""
from django.views import View
from eventos.models import Evento
from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect


class BasicView(UserPassesTestMixin, View):
    template_name = None

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return HttpResponseRedirect('/accounts/login')

    def get_context_data(self, user, *args, **kwargs):
        c = dict()
        c['usuario'] = user
        c['groups'] = [g.name for g in user.groups.all()]
        c['eventos'] = Evento.objects.all()
        c['back'] = '/'

        return c

    def get(self, request, c):
        return render(request, self.template_name, context=c)


class AdminView(BasicView):

    def handle_no_permission(self):
        return HttpResponseRedirect('/')

    def test_func(self):
        return self.request.user.groups.filter(name='admin').exists()
