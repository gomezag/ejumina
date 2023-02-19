from django.views import View
from eventos.models import Usuario, Evento
from django.shortcuts import render


class BasicView(View):
    template_name = None

    def get_context_data(self, user, *args, **kwargs):
        c = dict()
        c['usuario'] = Usuario.objects.get(user=user)
        c['eventos'] = Evento.objects.all()

        return c

    def get(self, request, c):
        return render(request, self.template_name, context=c)


class AdminView(BasicView):
    pass
