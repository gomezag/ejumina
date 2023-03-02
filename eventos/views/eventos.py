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
            c['edit_form'] = EventoForm(auto_id='edit')
        return super().get(request, c)

    def post(self, request):
        if not request.user.groups.filter(name='admin').exists():
            return self.get(request)
        c = self.get_context_data(request.user)
        if request.POST.get('delete', None) is not None:
            try:
                evento = Evento.objects.get(pk=request.POST['delete'])
                #evento.delete()
            except Exception as e:
                pass
            form = EventoForm()
        elif request.POST.get('edit', None) is not None:
            try:
                evento = Evento.objects.get(pk=request.POST['edit'])
                form = EventoForm(request.POST, instance=evento)
                if form.is_valid():
                    form.save()
            except ObjectDoesNotExist:
                form = EventoForm()
            c['edit_form'] = form
        else:
            form = EventoForm(request.POST)
            if form.is_valid():
                form.save()

        c['form'] = form
        return render(request, self.template_name, context=c)


class PanelEvento(BasicView):
    template_name = 'eventos/panel_evento.html'

    @staticmethod
    def parse_invitaciones(persona_set, evento):
        r = []
        for persona in persona_set:
            invitaciones = Invitacion.objects.filter(evento=evento, cliente=persona)
            frees = Free.objects.filter(evento=evento, cliente=persona)
            listas = ListaInvitados.objects.filter(Q(personas=persona, invitacion__evento=evento.pk) |
                                                       Q(personas_free=persona, free__evento=evento.pk)).distinct()
            r.append({'nombre': persona.nombre,
                                  'cedula': persona.cedula if persona.cedula else '',
                                  'pk': persona.pk,
                                  'invis': invitaciones.count(),
                                  'invis_usadas': invitaciones.filter(estado='USA').count(),
                                  'frees': frees.count(),
                                  'frees_usadas': frees.filter(estado='USA').count(),
                                  'listas': list(listas)})
        return r

    def get_context_data(self, user, evento=None, persona=None, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        if evento and not isinstance(evento, Evento):
            c['evento'] = Evento.objects.get(slug=evento)
        else:
            c['evento'] = Evento.objects.all()[0]

        c['personas'] = self.parse_invitaciones(Persona.objects.all(), c['evento'])

        if any([r in c['groups'] for r in ('rrpp', 'admin')]):
            c['invi_dadas'] = c['evento'].invitacion_set.filter(vendedor=c['usuario'],
                                                                evento=c['evento'].pk).exclude(cliente=None).count()
            c['frees_dados'] = c['evento'].free_set.filter(vendedor=c['usuario'],
                                                           evento=c['evento'].pk).exclude(cliente=None).count()
            c['frees_total'] = c['evento'].free_set.filter(vendedor=c['usuario'],
                                                           evento=c['evento'].pk).count()
        c['checkin_form'] = CheckInForm()
        return c

    def get(self, request, evento, *args, **kwargs):
        user = request.user
        # Check query
        persona = request.GET.get('persona', None)
        c = self.get_context_data(user, evento, persona)
        if any([r in c['groups'] for r in ('rrpp', 'admin')]):
            c['persona_form'] = InvitacionAssignForm(request.user, auto_id='invi_%s')

        return super().get(request, c)

    def post(self, request, evento, *args, **kwargs):
        evento = Evento.objects.get(slug=evento)
        user = request.user
        c = self.get_context_data(user, evento, None)
        checkin = request.POST.get('checkin', False)
        invitar = request.POST.get('invitar', False)
        if validate_in_group(c['groups'], ('rrpp', 'admin')) and invitar:
            form = InvitacionAssignForm(request.user, data=request.POST, auto_id='invi_%s')
            if form.is_valid():
                form.save(request.user, evento)
            c['persona_form'] = form

        elif validate_in_group(c['groups'], ('entrada', 'admin')) and checkin:
            checkin_form = CheckInForm(request.POST)
            print(request.POST['persona'])
            if checkin_form.is_valid(evento=evento):
                checkin_form.save()
            else:
                c['checkin_errors'] = checkin_form.errors
                print(c['checkin_errors'])
            c['persona_form'] = InvitacionAssignForm(request.user, auto_id='invi_%s')
        c.update(self.get_context_data(user, evento=evento))
        return render(request, self.template_name, context=c)


class PanelEventoPersona(BasicView):
    template_name = 'eventos/persona_view_evento.html'

    @staticmethod
    def parse_invitaciones(persona, evento):
        out = []
        invis = list(Invitacion.objects.filter(evento=evento, cliente=persona).
            values('vendedor__pk', 'lista__pk', 'lista__nombre').annotate(
            invis=Count('lista'),
            used_invis=Count('lista', filter=Q(estado='USA'))))
        frees = list(Free.objects.filter(evento=evento, cliente=persona).
            values('vendedor__pk', 'lista__pk', 'lista__nombre').annotate(
            frees=Count('lista'),
            used_frees=Count('lista', filter=Q(estado='USA'))))
        all_invis = sorted(list(itertools.chain(invis, frees)), key=lambda x: (x['vendedor__pk'], x['lista__pk']))
        for common, invis in itertools.groupby(all_invis, key=lambda x: (x['vendedor__pk'], x['lista__pk'])):
            lista = ListaInvitados.objects.get(pk=common[1])
            r = {
                'rrpp': Usuario.objects.get(pk=common[0]),
                'lista_id': lista.pk,
                'invis': 0,
                'frees': 0,
                'used_invis': 0,
                'used_frees': 0
            }
            [r.update(i) for i in invis]
            out.append(r)
        return out

    def get_context_data(self, user, persona, evento, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        c['back'] = '/e/{}'.format(evento.slug)
        invitaciones = persona.invitacion_set.filter(evento=evento)
        c['persona'] = persona
        c['evento'] = evento
        c['invitaciones'] = invitaciones
        c['frees'] = persona.free_set.filter(evento=evento)
        c['invitaciones'] = self.parse_invitaciones(persona, evento)
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
                if free.estado == 'ACT':
                    free.cliente = None
                    free.save()
            for invi in invitaciones:
                if invi.estado == 'USA':
                    invi.delete()
            form = MultiInviAssignToPersona(request.user, persona)
        elif request.POST.get('edit', None):
            pass
        else:
            form = MultiInviAssignToPersona(request.user, persona, data=request.POST)
            if form.is_valid():
                form.save(request.user, persona, evento)
        c = self.get_context_data(request.user, persona, evento)
        c['form'] = form
        return super().get(request, c)

