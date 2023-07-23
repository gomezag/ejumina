from eventos.models import *
from django.http.response import JsonResponse, HttpResponse
from django.views.generic import View
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin
import json


class BasicView(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated


class Personas(BasicView, View):

    def post(self, request):
        data = request.POST
        name = data.get('invi_persona', None)
        cedula = data.get('invi_cedula', None)
        personas = Persona.objects.all()
        print(name, cedula)
        print(request.POST)
        if not name and not cedula:
            return JsonResponse(data={'personas':[]})
        if name:
            personas = personas.filter(nombre__icontains=name)
        if cedula:
            personas = personas.filter(cedula__icontains=cedula)

        personas = [(p.nombre, p.cedula, p.pk) for p in personas]

        return JsonResponse(data={'personas': personas})


def get_listas_for_persona_and_evento(request):
    user = request.user
    listas = []
    if request.method == 'POST':
        data = request.POST
        persona = data.get('persona', None)
        evento = data.get('evento', None)
        if persona and evento:
            if validate_in_group(user, ('admin', 'entrada')):
                listas = ListaInvitados.objects.filter(Q(personas=persona, invitacion__evento=evento) |
                                                       Q(personas_free=persona, free__evento=evento)).distinct()
            else:
                listas = ListaInvitados.objects.filter(
                    Q(personas=persona, invitacion__evento=evento, invitacion__vendedor=user) |
                    Q(personas_free=persona, free__evento=evento, free__vendedor=user)).distinct()
        return JsonResponse({'listas': ', '.join([l.nombre for l in listas])}, status=200)
    else:
        return JsonResponse(status=403)

