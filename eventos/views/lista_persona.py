from django.views import View
from django.shortcuts import render
from eventos.models import Usuario, Grupo, Persona
from eventos.forms import PersonaForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ..forms import InvitacionAssignFormset


@method_decorator(login_required, name='get')
class ListaPersona(View):
    def get_context_data(self, user, persona=None):
        c = {}
        try:
            c['usuario'] = user.persona.nombre
        except AttributeError:
            c['usuario'] = ' cliente.'
        c['personas'] = Persona.objects.all()
        if persona is None:
            c['form'] = PersonaForm()
        else:
            c['form'] = PersonaForm(initial=persona)
        return c

    def get(self, request, *args, **kwargs):

        user = Usuario.objects.get(user=request.user)
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
                persona = form.save()
                grupos = form.cleaned_data.get('grupos')
                for grupo in grupos:
                    grupo.miembros.add(persona)
        return self.get(request)

