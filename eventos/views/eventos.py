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
from django.db.models import Count, Q, F, Value,  Case, When, IntegerField
from django.db.models.functions import Concat
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import itertools

from eventos.forms import EventoForm, InvitacionAssignForm, CheckInForm, MultiInviAssignToPersona, EventoDeleteForm, \
    FreeAssign
from eventos.views.basic_view import BasicView, AdminView
from eventos.utils import validate_in_group, mail_event_attendees
from eventos.models import Invitacion, Evento, ListaInvitados, Persona, Free, Usuario
from django.db import connection


class ListaEventos(BasicView):
    template_name = 'eventos/lista_eventos.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        if validate_in_group(user, ('admin',)):
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
        if not validate_in_group(request.user, ('admin', 'entrada')):
            return HttpResponseRedirect("")
        c = self.get_context_data(request.user)
        if request.POST.get('delete', None) is not None and validate_in_group(request.user, ('admin',)):
            try:
                evento = Evento.objects.get(pk=request.POST['delete'])
                if evento.estado == 'ACT':
                    evento.estado = 'INA'
                elif evento.estado == 'INA':
                    evento.estado = 'ACT'
                evento.save()
            except Exception as e:
                pass
        elif request.POST.get('delete_evento', None) is not None and validate_in_group(request.user, ('admin',)):
            try:
                evento_id = request.POST.get('delete_evento', None)
                if evento_id:
                    dform = EventoDeleteForm(request.POST)
                    if dform.is_valid(evento_id):
                        Evento.objects.get(pk=evento_id).delete()
                    else:
                        c['err_msg'] = ['El nombre escrito no coincide con el nombre del evento!']
            except ObjectDoesNotExist:
                c['err_msg'] = ['El evento no existe!']
        elif request.POST.get('edit', None) is not None and validate_in_group(request.user, ('admin',)):
            try:
                evento = Evento.objects.get(pk=request.POST['edit'])
                form = EventoForm(request.POST, instance=evento, auto_id='edit')
                if form.is_valid():
                    form.save()
                else:
                    c['err_msg'] = ['El formulario tuvo errores']
                c['edit_form'] = form
            except ObjectDoesNotExist:
                pass
        elif request.POST.get('mail_csv', None):
            try:
                evento = Evento.objects.get(pk=request.POST['mail_csv'])
                try:
                    brief_list, persona_set = PanelEvento.parse_invitaciones(evento, request.user)
                    persona_set = persona_set.annotate(
                        invis=Count('invitacion__pk',
                                    filter=Q(invitacion__evento=evento.pk), distinct=True
                                    ),
                        frees=Count('free__pk',
                                    filter=Q(free__evento=evento), distinct=True
                                    ),
                        used_invis=Count('invitacion__pk',
                                         filter=Q(invitacion__evento=evento, invitacion__estado='USA'), distinct=True
                                         ),
                        used_frees=Count('free__pk',
                                         filter=Q(free__evento=evento, free__estado='USA'), distinct=True
                                         ),
                    )
                    r = []
                    for person in persona_set:
                        listas = ListaInvitados.objects.filter(Q(personas=person, invitacion__evento=evento.pk) |
                                                               Q(personas_free=person,
                                                                 free__evento=evento.pk)).distinct()

                        r.append({'nombre': person.nombre,
                                  'cedula': person.cedula if person.cedula else '',
                                  'pk': person.pk,
                                  'invis': person.invis,
                                  'used_invis': person.used_invis,
                                  'frees': person.frees,
                                  'used_frees': person.used_frees,
                                  'listas': list(listas)})

                    if not r:
                        c['err_msg'] = ['No se encontraron invitaciones para este evento.']
                    else:
                        mail_event_attendees(request.user, r, evento)
                        c['alert_msg'] = ['Mail enviado con éxito!', ]
                except Exception as e:
                    print(e)
                    c['err_msg'] = ['Hubo un error al enviar el mail.']
            except ObjectDoesNotExist:
                pass
        elif validate_in_group(request.user, ('admin',)):
            form = EventoForm(request.POST)
            if form.is_valid():
                form.save()
            else:
                c['err_msg'] = ['El formulario tuvo errores.']
            c['form'] = form

        c['alert_msg'].extend(c.get('err_msg', []))
        if not c.get('err_msg'):
            self.request.session['alert_msg'] = c.get('alert_msg', [])
            return HttpResponseRedirect(self.request.path_info)
        else:
            return render(request, self.template_name, context=c)


class PanelEvento(BasicView):
    template_name = 'eventos/panel_evento.html'

    @staticmethod
    def get_lista_invitados(evento, user, persona=None, queryset=None):

        if not queryset:
            personas = Persona.objects.filter(estado='ACT')
            personas = personas.filter(Q(invitacion__evento=evento) | Q(free__evento=evento)).distinct()
        else:
            personas = queryset
        personas = personas.order_by('nombre')
        if persona:
            personas = personas.filter(Q(nombre__icontains=persona) | Q(cedula__icontains=persona))

        return personas

    @staticmethod
    def parse_invitaciones(evento, user, persona=None, queryset=None):
        personas = PanelEvento.get_lista_invitados(evento, user, persona=persona, queryset=queryset)
        full_list = personas.values('nombre', 'cedula', 'pk')

        return full_list, personas

    def get_context_data(self, user, evento=None, persona=None, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        if evento and not isinstance(evento, Evento):
            c['evento'] = Evento.objects.get(slug=evento)
        elif isinstance(evento, Evento):
            c['evento'] = evento
        else:
            c['evento'] = Evento.objects.filter(estado='ACT').first()

        full_list, personas = self.parse_invitaciones(evento, user, persona=persona)

        paginator = Paginator(personas, 20)
        page = paginator.get_page(kwargs.get('page', 1))
        persona_set = page.object_list

        if validate_in_group(user, ('admin', 'entrada')):
            persona_set = persona_set.annotate(
                invis=Count('invitacion__pk',
                            filter=Q(invitacion__evento=evento.pk), distinct=True
                            ),
                frees=Count('free__pk',
                            filter=Q(free__evento=evento), distinct=True
                            ),
                used_invis=Count('invitacion__pk',
                                 filter=Q(invitacion__evento=evento, invitacion__estado='USA'), distinct=True
                                 ),
                used_frees=Count('free__pk',
                                 filter=Q(free__evento=evento, free__estado='USA'), distinct=True
                                 ),
            )
        else:
            persona_set = persona_set.annotate(
                invis=Count('invitacion__pk',
                            filter=Q(invitacion__vendedor=user, invitacion__evento=evento.pk), distinct=True
                            ),
                frees=Count('free__pk',
                            filter=Q(free__vendedor=user, free__evento=evento), distinct=True
                            ),
                used_invis=Count('invitacion__pk',
                                 filter=Q(invitacion__vendedor=user, invitacion__evento=evento,
                                          invitacion__estado='USA'), distinct=True
                                 ),
                used_frees=Count('free__pk',
                                 filter=Q(free__vendedor=user, free__evento=evento, free__estado='USA'), distinct=True
                                 ),
            )

        r = []

        for person in persona_set:

            r.append({'nombre': person.nombre,
                      'cedula': person.cedula if person.cedula else '',
                      'pk': person.pk,
                      'invis': person.invis,
                      'used_invis': person.used_invis,
                      'frees': person.frees,
                      'used_frees': person.used_frees,
                      })

        page.object_list = r
        c['personas_invitadas'] = full_list
        if persona:
            c['query_key'] = persona
        c['personas_page'] = page
        if validate_in_group(user, ('admin', 'entrada')):
            c['invi_dadas'] = c['evento'].invitacion_set.filter(cliente__isnull=False).count()
            c['frees_dados'] = c['evento'].free_set.filter(cliente__isnull=False).count()
            c['frees_total'] = c['evento'].free_set.count()
            c['checked_in'] = c['evento'].invitacion_set.filter(estado='USA',
                                                                cliente__isnull=False).count()
            c['checked_in'] += c['evento'].free_set.filter(estado='USA',
                                                           cliente__isnull=False).count()
        else:
            c['invi_dadas'] = user.invitacion_set.filter(evento=c['evento'],
                                                         cliente__estado='ACT',
                                                         cliente__isnull=False, vendedor=user).count()
            c['frees_dados'] = user.free_set.filter(evento=c['evento'],
                                                    cliente__estado='ACT',
                                                    cliente__isnull=False, vendedor=user).count()
            c['frees_total'] = user.free_set.filter(evento=c['evento'], vendedor=user).count()
            c['checked_in'] = user.invitacion_set.filter(evento=c['evento'],
                                                         estado='USA',
                                                         cliente__estado='ACT',
                                                         cliente__isnull=False, vendedor=user).count()
            c['checked_in'] += user.free_set.filter(evento=c['evento'],
                                                    estado='USA',
                                                    cliente__estado='ACT',
                                                    cliente__isnull=False, vendedor=user).count()

        # [print(query['time'], query['sql']) for query in connection.queries]
        if validate_in_group(user, ('admin', 'entrada')):
            c['checkin_form'] = CheckInForm()
        return c

    def get(self, request, evento, *args, **kwargs):
        user = request.user
        evento = Evento.objects.get(slug=evento)
        if evento.estado != 'ACT' and (validate_in_group(user, ('admin',))):
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
        if evento.estado != 'ACT' and (validate_in_group(user, ('admin',))):
            HttpResponseRedirect('/')
        c = self.get_context_data(user, evento,
                                   persona=request.GET.get('persona', None),
                                   page=request.GET.get('page', None))
        c.update({'form_errors':[]})
        checkin = request.POST.get('checkin', False)
        invitar = request.POST.get('invitar', False)
        if validate_in_group(user, ('rrpp', 'admin')) and invitar:
            form = InvitacionAssignForm(request.user, data=request.POST, auto_id='invi_%s')
            if form.is_valid():
                form.save(request.user, evento)
                c['alert_msg'].extend(['Invitación guardada.'])
            else:
                c['form_errors'].extend(['Hubo problemas con el formulario.'])
            c['persona_form'] = form

        elif validate_in_group(user, ('entrada', 'admin')) and checkin:
            checkin_form = CheckInForm(request.POST)
            if checkin_form.is_valid(evento=evento):
                checkin_form.save()
                invis = checkin_form.cleaned_data['check_invis']
                frees = checkin_form.cleaned_data['check_frees']
                c['alert_msg'].extend(['Checked in: ', '{} Invitados y {} Frees'.format(invis, frees)])
            else:
                c['form_errors'].extend(checkin_form.errors)
            c['persona_form'] = InvitacionAssignForm(request.user, auto_id='invi_%s')

        if c.get('form_errors'):
            c['alert_msg'].extend(c.get('form_errors'))
            return render(request, self.template_name, context=c)
        else:
            self.request.session['alert_msg'] = c.get('alert_msg', [])
            return HttpResponseRedirect(self.request.path_info)


class PanelEventoPersona(BasicView):
    template_name = 'eventos/persona_view_evento.html'

    @staticmethod
    def parse_invitaciones(persona, evento, user):
        out = []
        if validate_in_group(user, ('admin', 'entrada')):
            invitaciones = Invitacion.objects.filter(evento=evento, cliente=persona)
            frees = Free.objects.filter(evento=evento, cliente=persona)
        else:
            invitaciones = Invitacion.objects.filter(evento=evento, cliente=persona, vendedor=user)
            frees = Free.objects.filter(evento=evento, cliente=persona, vendedor=user)
        invis = list(invitaciones.
        values('vendedor__pk', 'lista__pk', 'lista__nombre').annotate(
            invis=Count('lista'),
            used_invis=Count('lista', filter=Q(estado='USA'))))
        frees = list(frees.
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
        c['invitaciones'] = self.parse_invitaciones(persona, evento, user)
        if validate_in_group(self.request.user, ('admin', 'entrada')):
            c['checkin_form'] = CheckInForm()
        c['back'] = '/e/{}'.format(evento.slug)
        return c

    def get(self, request, persona, evento, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        evento = Evento.objects.get(slug=evento)
        if evento.estado != 'ACT' and (validate_in_group(request.user, ('admin',))):
            HttpResponseRedirect('/')
        c = self.get_context_data(request.user, persona, evento)
        usuario = request.user
        if validate_in_group(usuario, ('admin', 'entrada')):
            c['checkin_form'] = CheckInForm()
        if validate_in_group(usuario, ('admin', 'rrpp')):
            form = MultiInviAssignToPersona(request.user, persona, evento=evento)
            c['form'] = form
        return render(request, self.template_name, context=c)

    def post(self, request, persona, evento, *args, **kwargs):
        persona = Persona.objects.get(pk=persona)
        evento = Evento.objects.get(slug=evento)
        if evento.estado != 'ACT' and (validate_in_group(request.user, ('admin',))):
            HttpResponseRedirect('/')
        checkin = request.POST.get('checkin', None)
        delete = request.POST.get('delete', None)
        form = None
        c = self.get_context_data(request.user, persona, evento)
        c['form_errors'] = []
        if validate_in_group(request.user, ('rrpp', 'admin')) and delete:
            try:
                integer_validator(request.POST['lista'])
                integer_validator(request.POST['rrpp'])
                lista = ListaInvitados.objects.get(pk=request.POST['lista'])
                rrpp = Usuario.objects.get(pk=request.POST['rrpp'])
            except Exception as e:
                return HttpResponseRedirect('')
            if (not validate_in_group(request.user, ('admin',))) and (rrpp != request.user):
                c['form_errors'].append('No podes borrar entradas que no son tuyas!')
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
                        c['form_errors'].append('No se puede borrar una entrada usada!')
                for invi in invitaciones:
                    if invi.estado == 'ACT':
                        invi.delete()
                    else:
                        c['form_errors'].append('No se puede borrar una entrada usada!')
        elif validate_in_group(request.user, ('entrada', 'admin')) and checkin:
            id_lista = request.POST.get('id_lista')
            checkin_form = CheckInForm(request.POST, vendedor=checkin, lista=id_lista)
            if checkin_form.is_valid(evento=evento):
                checkin_form.save()
                invis = checkin_form.cleaned_data['check_invis']
                frees = checkin_form.cleaned_data['check_frees']
                c['alert_msg'] = ['Checked in: ', '{} Invitados y {} Frees'.format(invis, frees)]
            else:
                c['form_errors'] = checkin_form.errors
            c['checkin_form'] = checkin_form

        elif validate_in_group(request.user, ('rrpp', 'admin')):
            form = MultiInviAssignToPersona(request.user, persona, data=request.POST, evento=evento)
            if form.is_valid():
                form.save(request.user, persona, evento)
                c['alert_msg'] = [f"{form.cleaned_data['invitaciones']} invitaciones y {form.cleaned_data['frees']} frees registrados."]

        if not form:
            form = MultiInviAssignToPersona(request.user, persona, evento=evento)
            if not validate_in_group(request.user, ('admin',)):
                form.fields['frees'].widget.max_value = request.user.free_set.filter(estado='ACT', evento=evento,
                                                                               cliente__isnull=True).count()
        c['form'] = form
        if c.get('form_errors'):
            c['alert_msg'].extend(c.get('form_errors'))
            # alert_msg = c['alert_msg']
            # c.update(self.get_context_data(request.user, persona, evento))
            # c['alert_msg'] = alert_msg
            return render(request, self.template_name, context=c)
        else:
            self.request.session['alert_msg'] = c['alert_msg']
            return HttpResponseRedirect(self.request.path_info)


class PanelFrees(AdminView):
    template_name = 'eventos/panel_frees.html'

    def get_context_data(self, user, evento, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        evento = Evento.objects.get(slug=evento)
        users = Usuario.objects.filter(Q(groups__name='rrpp') | Q(groups__name='admin'))
        users = users.filter(is_superuser=False)
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
        success = False
        for user in c['users']:
            try:
                frees = int(request.POST[user.input_id])
                rrpp = Usuario.objects.get(pk=user.id)
                if frees > 0:
                    form = FreeAssign(data={'free': frees})
                    if form.is_valid():
                        form.save(request.user, rrpp, c['evento'])
                        success = True
                        success_msg = 'Free(s) asignado(s) con éxito.'
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
                            success = True
                            success_msg = 'Free(s) borrado(s) con éxito.'
                        except IndexError:
                            print('Se intentaron borrar mas frees de los que tenia un usuario')
                            pass
            except KeyError:
                pass
            except ValueError:
                pass
        c.update(**self.get_context_data(request.user, evento))
        if success:
            self.request.session['alert_msg'] = [success_msg]
            return HttpResponseRedirect(self.request.path_info)
        else:
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
        all_invis = sorted(list(itertools.chain(frees, )), key=lambda x: (x['cliente__pk'], x['lista__pk']))
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
        c = {'alert_msg': []}
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
