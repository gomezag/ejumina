from django.views import View
from eventos.models import Usuario


class BasicView(View):

    def get_context_data(self, user, *args, **kwargs):
        c = dict()
        c['usuario'] = Usuario.objects.get(user=user)

        return c

