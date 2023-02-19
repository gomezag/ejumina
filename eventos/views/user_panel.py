"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from eventos.forms import *
from django.db.models.base import ObjectDoesNotExist
from .basic_view import *


@method_decorator(login_required, name='get')
class PanelEvento(BasicView):
    template_name = 'eventos/panel_evento.html'

    def get_context_data(self, user, evento=None, persona=None, *args, **kwargs):
        c = super(PanelEvento, self).get_context_data(user, *args, **kwargs)
        if evento and not isinstance(evento, Evento):
            c['evento'] = Evento.objects.get(id=evento)
        else:
            c['evento'] = Evento.objects.all()[0]
        c['personas'] = []
        for persona in Persona.objects.all():
            try:
                invitaciones = Invitacion.objects.filter(evento=c['evento'], cliente=persona)
                frees = Free.objects.filter(evento=c['evento'], cliente=persona)
                listas = ListaInvitados.objects.filter(personas=persona).distinct()
            except ObjectDoesNotExist:
                invitaciones = listas = []

            c['personas'].append({'nombre': persona.nombre,
                                  'pk': persona.pk,
                                  'invitaciones': invitaciones.count(),
                                  'frees': frees.count(),
                                  'listas': list(listas)})
        c['invi_dadas'] = c['evento'].invitacion_set.filter(vendedor=c['usuario']).exclude(cliente=None)
        c['free_dados'] = c['evento'].free_set.filter(vendedor=c['usuario']).exclude(cliente=None)
        return c

    def get(self, request, evento, *args, **kwargs):
        user = request.user
        # Check query
        persona = request.GET.get('persona', None)
        c = self.get_context_data(user, evento, persona)
        c['persona_form'] = InvitacionAssignForm(usuario=c['usuario'])
        c['invi_totales'] = len(c['evento'].invitacion_set.all())

        return super().get(request, c)

    def post(self, request, evento, *args, **kwargs):

        evento = Evento.objects.get(id=evento)
        user = request.user
        c = self.get_context_data(user, evento, None)
        form = InvitacionAssignForm(request.POST, usuario=c['usuario'])

        if form.is_valid():
            form.save(evento, c['usuario'])

        c['persona_form'] = PersonaForm(evento)
        c['lista_form'] = form
        return super().get(request, c)


@method_decorator(login_required, name='get')
class PanelEventoPersona(BasicView):
    template_name = 'eventos/persona_view_evento.html'

    def get_context_data(self, user, persona, evento, *args, **kwargs):
        c = super(PanelEventoPersona, self).get_context_data(user, *args, **kwargs)
        invitaciones = persona.invitacion_set.filter(evento=evento)
        c['persona'] = persona
        c['evento'] = evento
        c['invitaciones'] = invitaciones
        c['frees'] = persona.free_set.filter(evento=evento)
        return c

    def get(self, request, persona, evento, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        evento = Evento.objects.get(pk=evento)
        c = self.get_context_data(request.user, persona, evento)
        usuario = Usuario.objects.get(user=request.user)
        c['form'] = MultiInviAssignToPersona(usuario, persona)
        return super().get(request, c)

    def post(self, request, persona, evento, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        evento = Evento.objects.get(pk=evento)
        form = MultiInviAssignToPersona(Usuario.objects.get(user=request.user), persona, data=request.POST)
        if form.is_valid():
            form.save(request.user, persona, evento)
        c = self.get_context_data(request.user, persona, evento)
        c['form'] = form
        return super().get(request, c)


@method_decorator(login_required, name='get')
class ListaUsuarios(AdminView):
    template_name = 'eventos/lista_usuarios.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super(ListaUsuarios, self).get_context_data(user)
        c['usuarios'] = Usuario.objects.all()
        return c

    def get(self, request, *args, **kwargs):
        c = self.get_context_data(request.user)

        return super().get(request, c)


@method_decorator(login_required, name='get')
class ListaEventos(BasicView):
    template_name = 'eventos/lista_eventos.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        c['eventos'] = Evento.objects.all()
        return c

    def get(self, request):
        user = request.user
        c = self.get_context_data(user)
        return super().get(request, c)


@method_decorator(login_required, name='get')
class PanelUsuario(AdminView):
    template_name = 'eventos/panel_usuario.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        id_usuario = kwargs.pop('id_usuario')
        c['id_usuario'] = Usuario.objects.get(id=id_usuario)
        c['id_eventos'] = []
        for evento in Evento.objects.all():
            c['id_eventos'].append({'frees_total': evento.free_set.filter(vendedor=c['id_usuario']).count(),
                                    'frees': evento.free_set.filter(vendedor=c['id_usuario'], cliente__isnull=False).count(),
                                    'invis': evento.invitacion_set.filter(vendedor=c['id_usuario']).count(),
                                    'nombre': evento.name,
                                    'id': evento.id})
        return c

    def get(self, request, *args, **kwargs):
        user = request.user
        c = self.get_context_data(user, *args, **kwargs)
        c['form'] = FreeAssignToUserForm()

        return super().get(request, c)

    def post(self, request, *args, **kwargs):
        id_vendedor = kwargs.get('id_usuario')
        vendedor = Usuario.objects.get(id=id_vendedor)
        user = Usuario.objects.get(user=request.user)
        form = FreeAssignToUserForm(request.POST)
        if form.is_valid():
            form.save(user, vendedor)
        c = self.get_context_data(request.user, *args, **kwargs)
        c['form'] = form
        return super().get(request, c)