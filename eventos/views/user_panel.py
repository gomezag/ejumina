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
from django.core import serializers

from eventos.forms import *
from eventos.views.basic_view import *
from eventos.utils import parse_excel_import


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
                                  'invitaciones': invitaciones.count(),
                                  'frees': frees.count(),
                                  'listas': list(listas)})
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
        c['persona_form'] = InvitacionAssignForm(request.user)
        c['invi_totales'] = len(c['evento'].invitacion_set.all())

        return super().get(request, c)

    def post(self, request, evento, *args, **kwargs):

        evento = Evento.objects.get(slug=evento)
        user = request.user
        form = InvitacionAssignForm(request.user, data=request.POST)

        if form.is_valid():
            form.save(request.user, evento)

        c = self.get_context_data(user, evento, None)
        c['persona_form'] = form
        return render(request, self.template_name, context=c)


class PanelEventoPersona(BasicView):
    template_name = 'eventos/persona_view_evento.html'

    def get_context_data(self, user, persona, evento, *args, **kwargs):
        c = super().get_context_data(user, *args, **kwargs)
        invitaciones = persona.invitacion_set.filter(evento=evento)
        c['persona'] = persona
        c['evento'] = evento
        c['invitaciones'] = invitaciones
        c['frees'] = persona.free_set.filter(evento=evento)
        c['invitaciones'] = []
        invis = list(Invitacion.objects.filter(evento=evento, cliente=persona).values('vendedor', 'lista').annotate(
            invis=Count('lista')))
        frees = list(Free.objects.filter(evento=evento, cliente=persona).values('vendedor', 'lista').annotate(
            frees=Count('lista')))
        all_invis = sorted(list(itertools.chain(invis, frees)), key=lambda x: (x['vendedor'], x['lista']))
        for common, group in itertools.groupby(all_invis, key=lambda x: (x['vendedor'], x['lista'])):
            vendedor = Usuario.objects.get(pk=common[0])
            lista = ListaInvitados.objects.get(pk=common[1])
            r = {
                'rrpp': vendedor.first_name,
                'lista_id': lista.pk,
                'invis': 0,
                'frees': 0,
            }
            [r.update(g) for g in group]
            r.update({'lista': lista.nombre})
            c['invitaciones'].append(r)

        c['back'] = '/e/{}'.format(evento.pk)
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


class PanelUsuario(AdminView):
    template_name = 'eventos/panel_usuario.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        id_usuario = kwargs.pop('id_usuario')
        c['id_usuario'] = Usuario.objects.get(id=id_usuario)
        c['id_eventos'] = []
        c['back'] = '/usuarios'
        for evento in Evento.objects.all():
            c['id_eventos'].append({'frees_total': evento.free_set.filter(vendedor=c['id_usuario']).count(),
                                    'frees': evento.free_set.filter(vendedor=c['id_usuario'],
                                                                    cliente__isnull=False).count(),
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
        user = request.user
        form = FreeAssignToUserForm(request.POST)
        if form.is_valid():
            form.save(user, vendedor)
        c = self.get_context_data(request.user, *args, **kwargs)
        c['form'] = form
        return super().get(request, c)


class ListaListasInvitados(AdminView):
    template_name = 'eventos/lista_listas_invitados.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        c['listas'] = ListaInvitados.objects.all()
        return c

    def get(self, request):
        user = request.user
        c = self.get_context_data(user)
        c['form'] = ListaInvitadosForm()
        return super().get(request, c)

    def post(self, request):
        c = self.get_context_data(request.user)
        form = ListaInvitadosForm(request.POST)
        if form.is_valid():
            form.save()
        c['form'] = form
        return render(request, self.template_name, context=c)


class ListaUsuarios(AdminView):
    template_name = 'eventos/lista_usuarios.html'

    def get_context_data(self, user, *args, **kwargs):
        c = super().get_context_data(user)
        c['usuarios'] = Usuario.objects.all()
        return c

    def get(self, request, *args, **kwargs):
        c = self.get_context_data(request.user)

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
        c['form'] = EventoForm()
        return super().get(request, c)

    def post(self, request):
        c = self.get_context_data(request.user)
        form = EventoForm(request.POST)
        if form.is_valid():
            form.save()
        c['form'] = form
        return render(request, self.template_name, context=c)


class ImportView(BasicView):
    template_name = 'eventos/excel_import.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        parsed_data = request.session.get('parsed_data', None)
        evento_pk = request.session.get('evento_pk', None)
        if parsed_data and evento_pk:
            evento = Evento.objects.get(pk=evento_pk)
            extras = {
                'invitaciones': parsed_data,
                'evento': evento
            }
        else:
            request.session.pop('parsed_data', None)
            request.session.pop('evento_pk', None)
            extras = {'form': ExcelImportForm()}
        c = self.get_context_data(user)
        c.update(extras)
        return render(request, self.template_name, context=c)

    def post(self, request, *args, **kwargs):
        user = request.user
        form = ExcelImportForm(request.POST, request.FILES)
        parsed = None
        evento_slug = None
        if form.is_valid():
            try:
                frees, res = parse_excel_import(request.FILES['file'])
            except ValueError as e:
                form.errors['file'] = [str(e)]
                res = False
            evento = form.cleaned_data['evento']
            total_frees = Free.objects.filter(vendedor=user, evento=evento, cliente__isnull=True).count()
            if frees > total_frees:
                form.errors['file'] = ["El excel asigna más frees de los que podes asignar al evento {}. Frees asignados:{}. Frees disponibles: {}.".format(
                    evento.name, frees, total_frees
                )]
                res = False
            if res:
                parsed = []
                for entry in res:
                    errors = []
                    try:
                        lista = ListaInvitados.objects.get(nombre=entry['lista'])
                        lista = {'nombre': lista.nombre, 'pk': lista.pk}
                    except ObjectDoesNotExist:
                        errors.append(('lista', 'Lista no existe. Se ignora esta entrada.'))
                        lista = {'nombre': entry['lista']}
                    try:
                        persona = Persona.objects.get(nombre=entry['nombre'])
                        persona = {'nombre': persona.nombre, 'pk': persona.pk}
                    except ObjectDoesNotExist:
                        errors.append(('persona', 'Persona no existe. Se creara nueva'))
                        persona = {'nombre': entry['nombre']}
                    frees = int(entry['frees'])
                    invis = int(entry['invis'])
                    if integer_validator(frees) and integer_validator(invis):
                        errors.append(('lista', "Error leyendo frees o invis. Se ignora esta entrada."))
                    parsed.append({
                        'persona': persona,
                        'lista': lista,
                        'frees': frees,
                        'invis': invis,
                        'errors': errors
                    })
                request.session.update({'parsed_data': parsed, 'evento_pk': evento.pk})
                return self.get(request)

        c = self.get_context_data(user)
        c['invitaciones'] = parsed
        c['form'] = form
        return render(request, self.template_name, context=c)


class ImportExcelToEvento(BasicView):
    def get(self, request):
        request.session.pop('parsed_data', None)
        request.session.pop('evento_pk', None)

        return HttpResponseRedirect('/importar')

    def post(self, request):
        parsed_data = request.session.pop('parsed_data', None)
        evento_pk = request.session.pop('evento_pk', None)
        evento = Evento.objects.get(pk=evento_pk)
        if parsed_data and evento:
            frees = list(Free.objects.filter(vendedor=request.user, evento=evento, cliente__isnull=True))
            for row in parsed_data:
                if 'lista' not in [r[0] for r in row['errors']]:
                    persona, created = Persona.objects.get_or_create(nombre=row['persona']['nombre'])
                    lista = ListaInvitados.objects.get(pk=row['lista']['pk'])
                    for n in range(row['invis']):
                        invi = Invitacion()
                        invi.vendedor = request.user
                        invi.cliente = persona
                        invi.lista = lista
                        invi.evento = evento
                        invi.save()
                    for n in range(row['frees']):
                        free = frees.pop(0)
                        free.cliente = persona
                        free.lista = lista
                        free.save()
        return HttpResponseRedirect('/e/{}'.format(evento.slug))
