"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""
import itertools

from django.db.models.base import ObjectDoesNotExist
from django.db.models import Count
from django.db.models import Q
from django.core.validators import integer_validator

from eventos.forms import *
from eventos.views.basic_view import *
from eventos.utils import validate_in_group


class PanelEvento(BasicView):
    template_name = 'eventos/panel_evento.html'

    def get_context_data(self, user, evento=None, persona=None, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        if evento and not isinstance(evento, Evento):
            c['evento'] = Evento.objects.get(slug=evento)
        else:
            c['evento'] = Evento.objects.all()[0]

        c['personas'] = []
        for persona in Persona.objects.all():
            try:
                invitaciones = Invitacion.objects.filter(evento=c['evento'], cliente=persona)
                frees = Free.objects.filter(evento=c['evento'], cliente=persona)
                listas = ListaInvitados.objects.filter(Q(personas=persona, invitacion__evento=c['evento'].pk) |
                                                       Q(personas_free=persona, free__evento=c['evento'].pk)).distinct()
            except ObjectDoesNotExist:
                invitaciones = listas = []

            c['personas'].append({'nombre': persona.nombre,
                                  'pk': persona.pk,
                                  'invis': invitaciones.count(),
                                  'invis_disponibles': invitaciones.filter(estado='ACT').count(),
                                  'frees': frees.count(),
                                  'frees_disponibles': frees.filter(estado='ACT').count(),
                                  'listas': list(listas)})

        if any([r in c['groups'] for r in ('rrpp', 'admin')]):
            c['invi_dadas'] = c['evento'].invitacion_set.filter(vendedor=c['usuario'],
                                                                evento=c['evento'].pk).exclude(cliente=None).count()
            c['frees_dados'] = c['evento'].free_set.filter(vendedor=c['usuario'],
                                                           evento=c['evento'].pk).exclude(cliente=None).count()
            c['frees_total'] = c['evento'].free_set.filter(vendedor=c['usuario'],
                                                           evento=c['evento'].pk).count()

        return c

    def get(self, request, evento, *args, **kwargs):
        user = request.user
        # Check query
        persona = request.GET.get('persona', None)
        c = self.get_context_data(user, evento, persona)
        if any([r in c['groups'] for r in ('rrpp', 'admin')]):
            c['persona_form'] = InvitacionAssignForm(request.user)

        return super().get(request, c)

    def post(self, request, evento, *args, **kwargs):

        evento = Evento.objects.get(slug=evento)
        user = request.user
        c = self.get_context_data(user, evento, None)
        checkin = request.POST.get('checkin', False)
        invitar = request.POST.get('invitar', False)
        if validate_in_group(c['groups'], ('rrpp', 'admin')) and invitar:
            form = InvitacionAssignForm(request.user, data=request.POST)
            if form.is_valid():
                form.save(request.user, evento)
            c['persona_form'] = form

        elif validate_in_group(c['groups'], ('entrada', 'admin')) and checkin:
            id_persona = request.POST.get('persona', None)
            persona = Persona.objects.get(pk=id_persona)
            n_invis = request.POST.get('n_invis', None)
            n_frees = request.POST.get('n_frees', None)

            checkin_form = CheckInForm({
                'evento': evento,
                'persona': persona,
                'check_invis': n_invis,
                'check_frees': n_frees
            })
            if checkin_form.is_valid():
                checkin_form.save()
            else:
                c['checkin_errors'] = checkin_form.errors
                print(c['checkin_errors'])
            c['persona_form'] = InvitacionAssignForm(request.user)
        c.update(self.get_context_data(user, evento=evento))
        return render(request, self.template_name, context=c)


class PanelEventoPersona(BasicView):
    template_name = 'eventos/persona_view_evento.html'

    def get_context_data(self, user, persona, evento, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        c['back'] = '/e/{}'.format(evento.slug)
        invitaciones = persona.invitacion_set.filter(evento=evento)
        c['persona'] = persona
        c['evento'] = evento
        c['invitaciones'] = invitaciones
        c['frees'] = persona.free_set.filter(evento=evento)
        c['invitaciones'] = []
        invis = list(Invitacion.objects.filter(evento=evento, cliente=persona).
                     values('vendedor__first_name', 'lista__pk', 'lista__nombre').annotate(
                     invis=Count('lista'),
                     used_invis=Count('lista', filter=Q(estado='USA'))))
        frees = list(Free.objects.filter(evento=evento, cliente=persona).
                     values('vendedor__first_name', 'lista__pk', 'lista__nombre').annotate(
                     frees=Count('lista'),
                     used_frees=Count('lista', filter=Q(estado='USA'))))
        all_invis = sorted(list(itertools.chain(invis, frees)), key=lambda x: (x['vendedor__first_name'], x['lista__pk']))
        for common, invis in itertools.groupby(all_invis, key=lambda x: (x['vendedor__first_name'], x['lista__pk'])):
            lista = ListaInvitados.objects.get(pk=common[1])
            r = {
                'rrpp': common[0],
                'lista_id': lista.pk,
                'invis': 0,
                'frees': 0,
                'used_invis': 0,
                'used_frees': 0
            }
            [r.update(i) for i in invis]
            c['invitaciones'].append(r)

        c['back'] = '/e/{}'.format(evento.slug)
        return c

    def get(self, request, persona, evento, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        evento = Evento.objects.get(slug=evento)
        c = self.get_context_data(request.user, persona, evento)
        usuario = request.user
        c['form'] = MultiInviAssignToPersona(usuario, persona)
        return super().get(request, c)

    def post(self, request, persona, evento, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        evento = Evento.objects.get(slug=evento)
        if request.POST.get('delete', None):
            try:
                integer_validator(request.POST['lista'])
                lista = ListaInvitados.objects.get(pk=request.POST['lista'])
            except Exception as e:
                return HttpResponseRedirect('/')
            invitaciones = Invitacion.objects.filter(cliente=persona, vendedor=request.user,
                                                     lista=lista)
            frees = Free.objects.filter(cliente=persona, vendedor=request.user,
                                        lista=lista)
            for free in frees:
                free.cliente = None
                free.save()
            for invi in invitaciones:
                invi.delete()
            form = MultiInviAssignToPersona(request.user, persona)
        else:
            form = MultiInviAssignToPersona(request.user, persona, data=request.POST)
            if form.is_valid():
                form.save(request.user, persona, evento)
        c = self.get_context_data(request.user, persona, evento)
        c['form'] = form
        return super().get(request, c)


class ListaEventos(BasicView):
    template_name = 'eventos/lista_eventos.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        c['eventos'] = Evento.objects.all()
        return c

    def get(self, request):
        user = request.user
        c = self.get_context_data(user)
        if request.user.groups.filter(name='admin').exists():
            c['form'] = EventoForm()
        return super().get(request, c)

    def post(self, request):
        if not request.user.groups.filter(name='admin').exists():
            return self.get(request)
        c = self.get_context_data(request.user)
        form = EventoForm(request.POST)
        if form.is_valid():
            form.save()
        c['form'] = form
        return render(request, self.template_name, context=c)
