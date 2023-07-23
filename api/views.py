from eventos.models import *
from django.http.response import JsonResponse
from django.views.generic import View
import json

# Create your views here.


class Personas(View):
    def post(self, request):
        data = request.POST
        name = data.get('invi-name', None)
        cedula = data.get('invi-cedula', None)
        personas = Persona.objects.all()
        if not name and not cedula:
            return JsonResponse(data={'personas':[]})
        if name:
            personas = personas.filter(nombre__icontains=name)
        if cedula:
            personas = personas.filter(cedula__icontains=cedula)

        personas = [(p.nombre, p.cedula, p.pk) for p in personas]

        return JsonResponse(data={'personas': personas})

