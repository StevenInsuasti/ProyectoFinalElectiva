"""
Vistas del módulo de reportes y dashboard analítico — Integrante 4.
"""

from __future__ import annotations

from datetime import timedelta
from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from accounts.decorators import administrador_requerido

from . import services


def _get_range(request):
    return services.parse_date_range(
        request.GET.get('fecha_desde'),
        request.GET.get('fecha_hasta'),
    )


@administrador_requerido
def analytics_dashboard(request):
    fecha_desde, fecha_hasta = _get_range(request)
    semana = services.ocupacion_semana_actual(fecha_desde, fecha_hasta)
    por_mes = services.reservas_por_mes(fecha_desde, fecha_hasta)
    por_sala = services.reservas_por_sala(fecha_desde, fecha_hasta)
    usuarios = services.indicadores_usuarios(fecha_desde, fecha_hasta)
    kpis = services.kpis_reservas(fecha_desde, fecha_hasta)

    context = {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'semana': semana,
        'por_mes': por_mes,
        'por_sala': por_sala,
        'usuarios': usuarios,
        'kpis': kpis,
    }
    return render(request, 'reporting/analytics_dashboard.html', context)


@administrador_requerido
def calendar_events_api(request):
    """
    Eventos para FullCalendar. Si vienen `start` y `end` (ISO), se usa ese rango
    (fin exclusivo según FullCalendar). Si no, se usan fecha_desde / fecha_hasta.
    """
    from django.utils.dateparse import parse_datetime

    start = parse_datetime(request.GET.get('start', ''))
    end = parse_datetime(request.GET.get('end', ''))
    if start and timezone.is_naive(start):
        start = timezone.make_aware(start, timezone.get_current_timezone())
    if end and timezone.is_naive(end):
        end = timezone.make_aware(end, timezone.get_current_timezone())

    if start and end:
        fecha_desde = start.date()
        # FullCalendar: `end` es exclusivo
        fecha_hasta = end.date() - timedelta(days=1)
        if fecha_hasta < fecha_desde:
            fecha_hasta = fecha_desde
    else:
        fecha_desde, fecha_hasta = services.parse_date_range(
            request.GET.get('fecha_desde'),
            request.GET.get('fecha_hasta'),
        )

    events = services.calendar_events_payload(fecha_desde, fecha_hasta)
    return JsonResponse(events, safe=False)


@administrador_requerido
def export_reservas_pdf(request):
    fecha_desde, fecha_hasta = _get_range(request)
    qs = list(services.reservas_todas_qs(fecha_desde, fecha_hasta).order_by('fecha', 'horario__hora_inicio'))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title='Reporte de reservas')
    styles = getSampleStyleSheet()
    story = [
        Paragraph(
            f'Reporte de reservas ({fecha_desde} — {fecha_hasta})',
            styles['Title'],
        ),
        Spacer(1, 12),
        Paragraph(
            f'Generado: {timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")}',
            styles['Normal'],
        ),
        Spacer(1, 18),
    ]

    data = [['Fecha', 'Espacio', 'Horario', 'Usuario', 'Estado']]
    for r in qs:
        hi = r.horario.hora_inicio.strftime('%H:%M')
        hf = r.horario.hora_fin.strftime('%H:%M')
        data.append(
            [
                r.fecha.isoformat(),
                r.espacio.nombre,
                f'{hi}–{hf}',
                r.usuario.get_nombre_completo(),
                r.get_estado_display(),
            ]
        )
    if len(data) == 1:
        data.append(['—', 'Sin datos en el rango', '', '', ''])

    tbl = Table(data, repeatRows=1, hAlign='LEFT')
    tbl.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]
        )
    )
    story.append(tbl)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_reservas.pdf"'
    return response


@administrador_requerido
def export_reservas_excel(request):
    fecha_desde, fecha_hasta = _get_range(request)
    qs = services.reservas_todas_qs(fecha_desde, fecha_hasta).order_by('fecha', 'horario__hora_inicio')

    wb = Workbook()
    ws = wb.active
    ws.title = 'Reservas'
    ws.append(
        [
            'Fecha',
            'Espacio',
            'Hora inicio',
            'Hora fin',
            'Usuario',
            'Email',
            'Estado',
            'Motivo',
        ]
    )
    for r in qs:
        ws.append(
            [
                r.fecha.isoformat(),
                r.espacio.nombre,
                r.horario.hora_inicio.strftime('%H:%M'),
                r.horario.hora_fin.strftime('%H:%M'),
                r.usuario.get_nombre_completo(),
                r.usuario.email,
                r.get_estado_display(),
                (r.motivo or '')[:500],
            ]
        )

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    response = HttpResponse(
        bio.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_reservas.xlsx"'
    return response
