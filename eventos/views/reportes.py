
from django.shortcuts import render
from django.db.models import Count, Q

from eventos.views.basic_view import BasicView, AdminView, SuperAdminView
from eventos.models import *
import json


class ReporteView(SuperAdminView):

    def get(self, request):
        c = self.get_context_data(request.user)
        eventos = Evento.objects.all().order_by('fecha')
        evento = Evento.objects.filter(name='BARBIE').last()
        rrpp = Usuario.objects.filter(Q(groups=Group.objects.get(name='rrpp')) | Q(groups=Group.objects.get(name='admin')))
        data = dict(values=[], labels=[], type='pie')
        for rp in rrpp:
            count = rp.invitacion_set.filter(evento=evento, estado='USA').count()
            if count:
                data['values'].append(count)
                data['labels'].append(rp.first_name)
        c['user_pie_data'] = json.dumps(data)

        trace_invis1 = dict(x=[], y=[], type='bar', marker=dict(color='rgb(75, 235, 102)'), name='Asistente')
        trace_invis2 = dict(x=[], y=[], type='bar', marker=dict(color='rgb(194, 242, 202)'), name='NoShow')
        trace_frees = dict(x=[], y=[], type='bar', marker=dict(color='rgb(96, 137, 247)'), name='Free')
        trace_frees2 = dict(x=[], y=[], type='bar', marker=dict(color='rgb(191, 206, 245)'), name='Free NoShow')

        points = []
        for rp in rrpp:
            points.append((rp.first_name, rp.invitacion_set.filter(estado='USA').count(),
                           rp.invitacion_set.filter(estado='ACT').count(),
                           rp.free_set.filter(estado='USA').count(),
                           rp.free_set.filter(estado='ACT').count()))
        lines = []
        for rp in rrpp:
            line = dict(x=[], y=[], text=[], type='bar', name=rp.first_name)
            for evento in eventos:
                invi_count = rp.invitacion_set.filter(estado='USA', evento=evento).count()
                invi_count += rp.free_set.filter(estado='USA', evento=evento).count()
                if invi_count:
                    line['x'].append(evento.fecha.strftime("%Y-%m-%d"))
                    line['y'].append(rp.invitacion_set.filter(estado='USA', evento=evento).count())
                    line['text'].append(' - '.join([evento.name, evento.fecha.strftime("%Y-%m-%d"), rp.first_name, str(invi_count)]))
            if line['x']:
                lines.append(line)

        points.sort(key=lambda x: (x[1], x[3], x[4], x[2]), reverse=True)
        points = [p for p in points if p[1]>0 or p[2]>0 or p[3]>0]
        trace_invis1['x'] = [p[0] for p in points]
        trace_invis2['x'] = [p[0] for p in points]
        trace_frees['x'] = [p[0] for p in points]
        trace_frees2['x'] = [p[0] for p in points]
        trace_invis1['y'] = [p[1] for p in points]
        trace_invis2['y'] = [p[2] for p in points]
        trace_frees['y'] = [p[3] for p in points]
        trace_frees2['y'] = [p[4] for p in points]
        data = [trace_invis1, trace_frees, trace_invis2, trace_frees2]
        c['user_bar_data'] = json.dumps(data)
        c['user_bar_data_title'] = 'Invitaciones'
        c['user_scatter_data'] = json.dumps(lines)

        Persona.objects.all().annotate(invitaciones=Count('invitados'))

        return render(request, 'eventos/reportes.html', c)
