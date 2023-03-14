"""
/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
"""
from django.db.models.base import ObjectDoesNotExist
from django.core.validators import integer_validator
from django.http import HttpResponseRedirect
from django.shortcuts import render

from eventos.forms import ExcelImportForm, InvitacionAssignForm
from eventos.models import Evento, Free, Persona, ListaInvitados
from eventos.views.basic_view import BasicView
from eventos.utils import parse_excel_import


class ImportView(BasicView):
    template_name = 'eventos/excel_import.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        parsed_data = request.session.get('parsed_data', None)
        evento_pk = request.session.get('evento_pk', None)
        import_errors = request.session.get('import_errors', None)
        if parsed_data and evento_pk:
            request.session.pop('import_errors', None)
            evento = Evento.objects.get(pk=evento_pk)
            extras = {
                'invitaciones': parsed_data,
                'evento': evento
            }
        else:
            request.session.pop('parsed_data', None)
            request.session.pop('evento_pk', None)
            extras = {'form': ExcelImportForm()}
            if import_errors:
                extras.update({'import_errors': import_errors})

        c = self.get_context_data(user)
        c.update(extras)
        return render(request, self.template_name, context=c)

    def post(self, request, *args, **kwargs):
        user = request.user
        form = ExcelImportForm(request.POST, request.FILES)
        parsed = None
        if form.is_valid():
            try:
                frees, res = parse_excel_import(request.FILES['file'])
            except ValueError as e:
                form.errors['file'] = [str(e)]
                frees = 0
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
                        lista = ListaInvitados.objects.get(nombre=entry['lista'], administradores__in=[request.user])
                        lista = {'nombre': lista.nombre, 'pk': lista.pk}
                    except ObjectDoesNotExist:
                        errors.append(('error', 'Lista no existe (o no tenés acceso).'))
                        lista = {'nombre': entry['lista']}
                    try:
                        if entry['cedula']:
                            cedula = str(entry['cedula']).replace('.', '')
                        else:
                            cedula = ''
                            raise AttributeError
                        persona = Persona.objects.get(cedula=cedula)
                        serialized_persona = {'nombre': persona.nombre,
                                   'pk': persona.pk,
                                   'cedula': entry['cedula']}

                        if persona.nombre != entry['nombre']:
                            errors.append(('error', 'Esta cedula ya existe o no se puede leer.'))
                            serialized_persona['nombre'] = entry['nombre']
                    except ObjectDoesNotExist:
                        errors.append(('warning', 'Persona no existe. Se creara nueva.'))
                        serialized_persona = {'nombre': entry['nombre'], 'cedula': entry['cedula']}
                    except AttributeError:
                        errors.append(('error', 'Cedula vacía o no se puede leer'))
                        serialized_persona = {'nombre': entry['nombre'], 'cedula': cedula}
                    frees = int(entry['frees'])
                    invis = int(entry['invis'])
                    if integer_validator(frees) and integer_validator(invis):
                        errors.append(('error', "Error leyendo frees o invis. Se ignora esta entrada."))
                    parsed.append({
                        'persona': serialized_persona,
                        'lista': lista,
                        'frees': frees,
                        'invis': invis,
                        'errors': errors
                    })
                request.session.update({'parsed_data': parsed, 'evento_pk': evento.pk})
                form = None

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
        errors = []
        if parsed_data and evento:
            for row in parsed_data:
                if 'error' not in [r[0] for r in row['errors']]:
                    form = InvitacionAssignForm(request.user, data={
                        'persona': row['persona']['nombre'],
                        'lista': row['lista']['pk'],
                        'frees': row['frees'],
                        'cedula': row['persona']['cedula'].replace('.', ''),
                        'invitaciones': row['invis'],
                        'invitar': True
                    })
                    if form.is_valid():
                        form.save(request.user, evento)
                    else:
                        errors.append((row['persona']['nombre'], row['lista']['nombre'], form.errors))
        if errors:
            request.session.update({'import_errors': errors})
            return HttpResponseRedirect('/importar')
        return HttpResponseRedirect('/e/{}'.format(evento.slug))
