"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""
from django.core.validators import integer_validator
from django.db.models.base import ObjectDoesNotExist
from django.db.models import Count, Q, F, Value, Case, When, IntegerField, Aggregate, CharField, Subquery, Prefetch, OuterRef, JSONField, QuerySet, prefetch_related_objects
from django.db.models.functions import Concat
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from django.core.paginator import Paginator
import json
from django.http import HttpResponseRedirect
from django.shortcuts import render
import itertools

from eventos.forms import EventoForm, InvitacionAssignForm, CheckInForm, MultiInviAssignToPersona, EventoDeleteForm, FreeAssign
from eventos.views.basic_view import BasicView, AdminView
from eventos.utils import validate_in_group
from eventos.models import Invitacion, Evento, ListaInvitados, Persona, Free, Usuario


class ListaEventos(BasicView):
    template_name = 'eventos/lista_eventos.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        if validate_in_group(user, ('admin', )):
            c['eventos'] = Evento.objects.all().order_by('estado', '-fecha')
        else:
            c['eventos'] = Evento.objects.filter(estado='ACT').order_by('-fecha')
        if user.groups.filter(name='admin').exists():
            c['form'] = EventoForm()
            c['edit_form'] = EventoForm(auto_id='edit')
            c['delete_form'] = EventoDeleteForm(auto_id='delete')
        return c

    def get(self, request, **kwargs):
        user = request.user
        extras = kwargs.pop('extras', None)
        c = self.get_context_data(user)
        if extras:
            c.update(extras)
        return super().get(request, c)

    def post(self, request):
        if not request.user.groups.filter(name='admin').exists():
            return self.get(request, extras={'alert_msg': ['No autorizado']})
        c = self.get_context_data(request.user)
        if request.POST.get('delete', None) is not None:
            try:
                evento = Evento.objects.get(pk=request.POST['delete'])
                if evento.estado == 'ACT':
                    evento.estado = 'INA'
                elif evento.estado == 'INA':
                    evento.estado = 'ACT'
                evento.save()
            except Exception as e:
                pass
        elif request.POST.get('delete_evento', None) is not None:
            try:
                evento_id = request.POST.get('delete_evento', None)
                if evento_id:
                    dform = EventoDeleteForm(request.POST)
                    if dform.is_valid(evento_id):
                        Evento.objects.get(pk=evento_id).delete()
                    else:
                        c['alert_msg'] = ['El nombre escrito no coincide con el nombre del evento!']
            except ObjectDoesNotExist:
                c['alert_msg'] = ['El evento no existe!']
        elif request.POST.get('edit', None) is not None:
            try:
                evento = Evento.objects.get(pk=request.POST['edit'])
                form = EventoForm(request.POST, instance=evento, auto_id='edit')
                if form.is_valid():
                    form.save()
                else:
                    c['alert_msg'] = ['El formulario tuvo errores']
                c['edit_form'] = form
            except ObjectDoesNotExist:
                pass
        else:
            form = EventoForm(request.POST)
            if form.is_valid():
                form.save()
            else:
                c['alert_msg'] = ['El formulario tuvo errores.']
            c['form'] = form
        return render(request, self.template_name, context=c)


class PanelEvento(BasicView):
    template_name = 'eventos/panel_evento.html'

    @staticmethod
    def parse_invitaciones(persona_set, evento):
        r = []
        for persona in persona_set:
            listas = ListaInvitados.objects.filter(Q(personas=persona, invitacion__evento=evento.pk) |
                                                       Q(personas_free=persona, free__evento=evento.pk)).distinct()
            r.append({'nombre': persona.nombre,
                      'cedula': persona.cedula if persona.cedula else '',
                      'pk': persona.pk,
                      'invis': persona.invis,
                      'used_invis': persona.used_invis,
                      'frees': persona.frees,
                      'used_frees': persona.used_frees,
                      'listas': list(listas)})
        return r

    def get_context_data(self, user, evento=None, persona=None, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        if evento and not isinstance(evento, Evento):
            c['evento'] = Evento.objects.get(slug=evento)
        elif isinstance(evento, Evento):
            c['evento'] = evento
        else:
            c['evento'] = Evento.objects.all()[0]

        #TODO: En vez de ocultar, marcarlas en gris y sin link
        personas = Persona.objects.filter(estado='ACT')

        if validate_in_group(user, ('admin', 'entrada')):
            personas = personas.annotate(
                invis=Count(
                    Case(
                        When(
                            invitacion__evento=evento.pk, then=1
                        ),
                        output_field=IntegerField()
                    )
                ),
                frees=Count(
                    Case(
                        When(
                            free__vendedor=user, free__evento=evento, then=1
                        ),
                        output_field=IntegerField()
                    )
                ),
                used_invis=Count(
                    Case(
                        When(
                            invitacion__evento=evento, invitacion__estado='USA', then=1
                        ),
                        output_field=IntegerField()
                    )
                ),
                used_frees=Count(
                    Case(
                        When(
                            free__evento=evento, free__estado='USA', then=1
                        ),
                        output_field=IntegerField()
                    )
                ),
            )
        else:
            personas = personas.annotate(
                invis=Count(
                    Case(
                        When(
                            invitacion__vendedor=user, invitacion__evento=evento, then=1
                        ),
                        output_field=IntegerField()
                    )
                ),
                frees=Count(
                    Case(
                        When(
                            free__vendedor=user, free__evento=evento, then=1
                        ),
                        output_field=IntegerField()
                    )
                ),
                used_invis=Count(
                    Case(
                        When(
                            invitacion__vendedor=user, invitacion__evento=evento, invitacion__estado='USA',  then=1
                        ),
                        output_field=IntegerField()
                    )
                ),
                used_frees=Count(
                    Case(
                        When(
                            free__vendedor=user, free__evento=evento, free__estado='USA', then=1
                        ),
                        output_field=IntegerField()
                    )
                ),
            )
        personas = personas.filter(Q(invis__gt=0)|Q(frees__gt=0))
        personas = personas.order_by('nombre')

        c['personas_invitadas'] = personas.values('nombre', 'cedula', 'pk')
        if persona:
            personas = personas.filter(Q(nombre__icontains=persona)|Q(cedula__icontains=persona))
            c['query_key'] = persona
        personas = self.parse_invitaciones(personas, evento)
        paginator = Paginator(personas, 20)
        persona_set = paginator.get_page(kwargs.get('page', 1))
        c['personas_query'] = Persona.objects.all().values('nombre', 'cedula', 'pk')
        c['personas_page'] = persona_set

        if any([r in c['groups'] for r in ('rrpp', 'admin')]):
            c['invi_dadas'] = c['evento'].invitacion_set.filter(vendedor=c['usuario'],
                                                                evento=c['evento'],
                                                                cliente__estado='ACT',
                                                                cliente__isnull=False).count()
            c['frees_dados'] = c['evento'].free_set.filter(vendedor=c['usuario'],
                                                           evento=c['evento'],
                                                           cliente__estado='ACT',
                                                           cliente__isnull=False).count()
            c['frees_total'] = c['evento'].free_set.filter(vendedor=c['usuario'],
                                                           evento=c['evento']).count()
            c['checked_in'] = user.invitacion_set.filter(evento=c['evento'],
                                                         estado='USA',
                                                         cliente__estado='ACT',
                                                         cliente__isnull=False).count()
            c['checked_in'] += user.free_set.filter(evento=c['evento'],
                                                    estado='USA',
                                                    cliente__estado='ACT',
                                                    cliente__isnull=False).count()

        if validate_in_group(user, ('admin', 'entrada')):
            c['checkin_form'] = CheckInForm()
        return c

    def get(self, request, evento, *args, **kwargs):
        user = request.user
        evento = Evento.objects.get(slug=evento)
        if evento.estado != 'ACT' and (validate_in_group(user, ('admin', ))):
            HttpResponseRedirect('/')
        c = self.get_context_data(user, evento,
                                  persona=request.GET.get('persona', None),
                                  page=request.GET.get('page', None))

        if any([r in c['groups'] for r in ('rrpp', 'admin')]):
            form = InvitacionAssignForm(request.user, auto_id='invi_%s', evento=evento)
            c['persona_form'] = form

        return render(request, self.template_name, context=c)

    def post(self, request, evento, *args, **kwargs):
        evento = Evento.objects.get(slug=evento)
        user = request.user
        if evento.estado != 'ACT' and (validate_in_group(user, ('admin', ))):
            HttpResponseRedirect('/')
        c = {}
        checkin = request.POST.get('checkin', False)
        invitar = request.POST.get('invitar', False)
        if validate_in_group(user, ('rrpp', 'admin')) and invitar:
            form = InvitacionAssignForm(request.user, data=request.POST, auto_id='invi_%s')
            if form.is_valid():
                form.save(request.user, evento)
            c['persona_form'] = form

        elif validate_in_group(user, ('entrada', 'admin')) and checkin:
            checkin_form = CheckInForm(request.POST)
            if checkin_form.is_valid(evento=evento):
                checkin_form.save()
                invis = checkin_form.cleaned_data['check_invis']
                frees = checkin_form.cleaned_data['check_frees']
                c['alert_msg'] = ['Checked in: ', '{} Invitados y {} Frees'.format(invis, frees)]
            else:
                c['checkin_errors'] = checkin_form.errors
                print(c['checkin_errors'])
            c['persona_form'] = InvitacionAssignForm(request.user, auto_id='invi_%s')
        c.update(self.get_context_data(user, evento,
                                  persona=request.GET.get('persona', None),
                                  page=request.GET.get('page', None)))
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
                'persona': persona,
                'rrpp': Usuario.objects.get(pk=common[0]),
                'lista_id': lista.pk,
                'invis': 0,
                'frees': 0,
                'used_invis': 0,
                'used_frees': 0,
                'evento': evento
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
        if evento.estado != 'ACT' and (validate_in_group(request.user, ('admin', ))):
            HttpResponseRedirect('/')
        c = self.get_context_data(request.user, persona, evento)
        usuario = request.user
        if validate_in_group(usuario, ('admin', 'entrada')):
            c['checkin_form'] = CheckInForm()
        return render(request, self.template_name, context=c)

    def post(self, request, persona, evento, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        evento = Evento.objects.get(slug=evento)
        if evento.estado != 'ACT' and (validate_in_group(request.user, ('admin', ))):
            HttpResponseRedirect('/')
        checkin = request.POST.get('checkin', None)
        delete = request.POST.get('delete', None)
        form = None
        c = self.get_context_data(request.user, persona, evento)
        c['alert_msg'] = []
        if validate_in_group(request.user, ('rrpp', 'admin')) and delete:
            try:
                integer_validator(request.POST['lista'])
                integer_validator(request.POST['rrpp'])
                lista = ListaInvitados.objects.get(pk=request.POST['lista'])
                rrpp = Usuario.objects.get(pk=request.POST['rrpp'])
            except Exception as e:
                return HttpResponseRedirect('')
            if (not validate_in_group(request.user, ('admin', ))) and (rrpp != request.user):
                c['alert_msg'].append('No podes borrar entradas que no son tuyas!')
            else:
                invitaciones = Invitacion.objects.filter(cliente=persona, vendedor=rrpp,
                                                         lista=lista, evento=evento)
                frees = Free.objects.filter(cliente=persona, vendedor=rrpp,
                                            lista=lista, evento=evento)

                for free in frees:
                    if free.estado == 'ACT':
                        if free.vendedor.groups.filter(name='admin').exists():
                            free.delete()
                        else:
                            free.cliente = None
                            free.save()
                    else:
                        c['alert_msg'] = ['No se puede borrar una entrada usada!']
                for invi in invitaciones:
                    if invi.estado == 'ACT':
                        invi.delete()
                    else:
                        c['alert_msg'] = ['No se puede borrar una entrada usada!']
        elif validate_in_group(request.user, ('entrada', 'admin')) and checkin:
            id_lista = request.POST.get('id_lista')
            checkin_form = CheckInForm(request.POST, vendedor=checkin, lista=id_lista)
            print(checkin, id_lista, evento)
            if checkin_form.is_valid(evento=evento):
                checkin_form.save()
                invis = checkin_form.cleaned_data['check_invis']
                frees = checkin_form.cleaned_data['check_frees']
                c['alert_msg'] = ['Checked in: ', '{} Invitados y {} Frees'.format(invis, frees)]
            else:
                c['checkin_errors'] = checkin_form.errors
                print(checkin_form.errors)
            c['checkin_form'] = checkin_form
        elif validate_in_group(request.user, ('rrpp', 'admin')):
            form = MultiInviAssignToPersona(request.user, persona, data=request.POST)
            if form.is_valid():
                form.save(request.user, persona, evento)

        c.update(self.get_context_data(request.user, persona, evento))
        if not form:
            form = MultiInviAssignToPersona(request.user, persona)
        c['form'] = form
        return render(request, self.template_name, context=c)


class PanelFrees(AdminView):
    template_name = 'eventos/panel_frees.html'

    def get_context_data(self, user, evento, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        evento = Evento.objects.get(slug=evento)
        users = Usuario.objects.filter(Q(groups__name='rrpp')|Q(groups__name='admin'))
        users = users.annotate(free_count=Count('free', filter=Q(free__evento=evento)),
                                    usedfree_count=Count('free', filter=Q(free__cliente__isnull=False,
                                                                           free__evento=evento)),
                                    input_id=Concat(F('username'), Value("_frees"))).order_by('first_name')
        c['users'] = users
        c['evento'] = evento
        return c

    def get(self, request, evento, *args, **kwargs):
        c = self.get_context_data(request.user, evento)
        return render(request, self.template_name, context=c)

    def post(self, request, evento, *args, **kwargs):
        c = self.get_context_data(request.user, evento)
        for user in c['users']:
            try:
                frees = int(request.POST[user.input_id])
                rrpp = Usuario.objects.get(pk=user.id)
                if frees > 0:
                    form = FreeAssign(data={'free': frees})
                    if form.is_valid():
                        form.save(request.user, rrpp, c['evento'])
                    else:
                        print('FreeAssign Errors:')
                        print(form.errors)
                        print('End FreeAssign Errors')
                elif frees < 0:
                    free_list = list(Free.objects.filter(vendedor=rrpp, evento=c['evento'], cliente__isnull=True))
                    for n in range(-frees):
                        try:
                            free = free_list[n]
                            free.delete()
                        except IndexError:
                            print('Se intentaron borrar mas frees de los que tenia un usuario')
                            pass
            except KeyError:
                pass
            except ValueError:
                pass
        c.update(**self.get_context_data(request.user, evento))
        return render(request, self.template_name, context=c)


class PanelEventoUsuario(AdminView):
    template_name = 'eventos/rrpp_view_evento.html'

    @staticmethod
    def parse_invitaciones(rrpp, evento):
        out = []
        frees = list(Free.objects.filter(evento=evento, vendedor=rrpp, cliente__isnull=False).
            values('cliente__pk', 'lista__pk', 'lista__nombre').annotate(
            frees=Count('lista'),
            used_frees=Count('lista', filter=Q(estado='USA'))))
        all_invis = sorted(list(itertools.chain(frees,)), key=lambda x: (x['cliente__pk'], x['lista__pk']))
        if len(all_invis) > 0:
            for common, invis in itertools.groupby(all_invis, key=lambda x: (x['cliente__pk'], x['lista__pk'])):
                lista = ListaInvitados.objects.get(pk=common[1])
                r = {
                    'rrpp': rrpp,
                    'persona': Persona.objects.get(pk=common[0]),
                    'lista_id': lista.pk,
                    'invis': 0,
                    'frees': 0,
                    'used_invis': 0,
                    'used_frees': 0
                }
                [r.update(i) for i in invis]
                out.append(r)
        else:
          out = []
        return out

    def get_context_data(self, user, rrpp, evento, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        c['back'] = '/e/{}/frees'.format(evento.slug)
        invitaciones = rrpp.invitacion_set.filter(evento=evento)
        c['rrpp'] = rrpp
        c['evento'] = evento
        c['invitaciones'] = invitaciones
        c['frees'] = rrpp.free_set.filter(evento=evento)
        c['invitaciones'] = self.parse_invitaciones(rrpp, evento)
        return c

    def get(self, request, rrpp, evento, *args, **kwargs):
        rrpp = Usuario.objects.get(pk=rrpp)
        evento = Evento.objects.get(slug=evento)
        c = self.get_context_data(request.user, rrpp, evento)
        c['checkin_form'] = CheckInForm()
        return render(request, self.template_name, context=c)

    def post(self, request, rrpp, evento, *args, **kwargs):
        rrpp = Usuario.objects.get(pk=rrpp)
        evento = Evento.objects.get(slug=evento)
        checkin = request.POST.get('checkin', None)
        delete = request.POST.get('delete', None)
        c = {'alert_msg':[]}
        if delete:
            try:
                integer_validator(request.POST['lista'])
                integer_validator(request.POST['persona'])
                lista = ListaInvitados.objects.get(pk=request.POST['lista'])
                persona = Persona.objects.get(pk=request.POST['persona'])
            except Exception as e:
                return HttpResponseRedirect('/')

            frees = Free.objects.filter(cliente=persona, vendedor=rrpp,
                                        lista=lista, evento=evento)

            for free in frees:
                if free.estado == 'ACT':
                    if free.vendedor.groups.filter(name='admin').exists():
                        free.delete()
                    else:
                        free.cliente = None
                        free.save()
                else:
                    c['alert_msg'] = ['No se puede borrar una entrada usada!']
        elif checkin:
            id_lista = request.POST.get('lista')
            checkin_form = CheckInForm(request.POST, vendedor=rrpp, lista=id_lista)
            if checkin_form.is_valid(evento=evento):
                checkin_form.save()
                invis = checkin_form.cleaned_data['check_invis']
                frees = checkin_form.cleaned_data['check_frees']
                c['alert_msg'] = ['Checked in: ', '{} Invitados y {} Frees'.format(invis, frees)]
            else:
                c['checkin_errors'] = checkin_form.errors
            c['checkin_form'] = checkin_form
        if not c.get('checkin_form', None):
            c['checkin_form'] = CheckInForm()
        c.update(self.get_context_data(request.user, rrpp, evento))
        return render(request, self.template_name, context=c)

