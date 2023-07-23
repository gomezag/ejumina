from eventos.models import *
from django.http.response import JsonResponse
from django.views.generic import View
import json

# Create your views here.


class Personas(View):
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

