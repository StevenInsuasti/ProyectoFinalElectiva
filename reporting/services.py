"""
Consultas agregadas para el dashboard de analítica (Integrante 4).
Optimizadas con select_related / values / annotate sobre datos reales.
"""

from __future__ import annotations

MESES_ES = (
    '',
    'Ene',
    'Feb',
    'Mar',
    'Abr',
    'May',
    'Jun',
    'Jul',
    'Ago',
    'Sep',
    'Oct',
    'Nov',
    'Dic',
)
from datetime import date, datetime, timedelta
from typing import Any

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from accounts.models import CustomUser
from reservas.models import Reserva


def _default_range() -> tuple[date, date]:
    """Rango por defecto: mes en curso completo (del día 1 al último día del mes)."""
    import calendar
    today = timezone.localdate()
    start = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end = today.replace(day=last_day)
    return start, end


def parse_date_range(
    fecha_desde_raw: str | None,
    fecha_hasta_raw: str | None,
) -> tuple[date, date]:
    """Parsea fechas desde query params; si fallan, usa el mes en curso hasta hoy."""
    from django.utils.dateparse import parse_date

    d_start, d_end = _default_range()
    if fecha_desde_raw:
        parsed = parse_date(fecha_desde_raw)
        if parsed:
            d_start = parsed
    if fecha_hasta_raw:
        parsed = parse_date(fecha_hasta_raw)
        if parsed:
            d_end = parsed
    if d_start > d_end:
        d_start, d_end = d_end, d_start
    return d_start, d_end


def reservas_no_canceladas_qs(fecha_desde: date, fecha_hasta: date):
    return (
        Reserva.objects.filter(fecha__gte=fecha_desde, fecha__lte=fecha_hasta)
        .exclude(estado=Reserva.ESTADO_CANCELADA)
        .select_related('espacio', 'horario', 'usuario')
    )


def reservas_todas_qs(fecha_desde: date, fecha_hasta: date):
    return Reserva.objects.filter(fecha__gte=fecha_desde, fecha__lte=fecha_hasta).select_related(
        'espacio', 'horario', 'usuario'
    )


def ocupacion_semanal_labels_es() -> list[str]:
    return ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']


def ocupacion_semana_actual(fecha_desde: date, fecha_hasta: date) -> dict[str, Any]:
    """
    Conteo de reservas no canceladas por día de la semana (0=lun … 6=dom)
    dentro de la intersección del rango solicitado y la semana ISO de fecha_hasta.
    """
    hoy = fecha_hasta
    # Lunes como inicio de semana (weekday: lunes=0)
    lunes = hoy - timedelta(days=hoy.weekday())
    domingo = lunes + timedelta(days=6)
    r0 = max(fecha_desde, lunes)
    r1 = min(fecha_hasta, domingo)
    counts = {i: 0 for i in range(7)}
    if r0 <= r1:
        qs = (
            reservas_no_canceladas_qs(r0, r1)
            .values_list('fecha', flat=True)
        )
        for f in qs:
            wd = f.weekday()
            counts[wd] = counts.get(wd, 0) + 1
    return {
        'labels': ocupacion_semanal_labels_es(),
        'data': [counts[i] for i in range(7)],
        'week_start': lunes.isoformat(),
        'week_end': domingo.isoformat(),
    }


def reservas_por_sala(fecha_desde: date, fecha_hasta: date) -> list[dict[str, Any]]:
    rows = (
        reservas_no_canceladas_qs(fecha_desde, fecha_hasta)
        .values('espacio_id', 'espacio__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    return [{'nombre': r['espacio__nombre'], 'total': r['total']} for r in rows]


def reservas_por_mes(fecha_desde: date, fecha_hasta: date) -> dict[str, Any]:
    qs = (
        reservas_no_canceladas_qs(fecha_desde, fecha_hasta)
        .annotate(m=TruncMonth('fecha'))
        .values('m')
        .annotate(total=Count('id'))
        .order_by('m')
    )
    labels: list[str] = []
    data: list[int] = []
    for row in qs:
        m = row['m']
        if m is None:
            continue
        labels.append(f'{MESES_ES[m.month]} {m.year}')
        data.append(row['total'])
    return {'labels': labels, 'data': data}


def indicadores_usuarios(fecha_desde: date, fecha_hasta: date) -> dict[str, int]:
    cuentas_activas = CustomUser.objects.filter(is_active=True).count()
    con_reserva = (
        reservas_no_canceladas_qs(fecha_desde, fecha_hasta)
        .values('usuario_id')
        .distinct()
        .count()
    )
    nuevos_en_rango = CustomUser.objects.filter(
        date_joined__date__gte=fecha_desde,
        date_joined__date__lte=fecha_hasta,
    ).count()
    return {
        'cuentas_activas': cuentas_activas,
        'usuarios_distintos_con_reserva': con_reserva,
        'registros_nuevos_en_rango': nuevos_en_rango,
    }


def kpis_reservas(fecha_desde: date, fecha_hasta: date) -> dict[str, int]:
    base = Reserva.objects.filter(fecha__gte=fecha_desde, fecha__lte=fecha_hasta)
    return {
        'total': base.count(),
        'pendientes': base.filter(estado=Reserva.ESTADO_PENDIENTE).count(),
        'aprobadas': base.filter(estado=Reserva.ESTADO_APROBADA).count(),
        'canceladas': base.filter(estado=Reserva.ESTADO_CANCELADA).count(),
    }


def calendar_events_payload(
    fecha_desde: date,
    fecha_hasta: date,
) -> list[dict[str, Any]]:
    """Estructura compatible con FullCalendar (eventos de un día)."""
    out: list[dict[str, Any]] = []
    colors = {
        Reserva.ESTADO_PENDIENTE: '#f0ad4e',
        Reserva.ESTADO_APROBADA: '#5cb85c',
        Reserva.ESTADO_CANCELADA: '#d9534f',
    }
    for r in reservas_todas_qs(fecha_desde, fecha_hasta):
        start = timezone.make_aware(
            datetime.combine(r.fecha, r.horario.hora_inicio),
            timezone.get_current_timezone(),
        )
        end = timezone.make_aware(
            datetime.combine(r.fecha, r.horario.hora_fin),
            timezone.get_current_timezone(),
        )
        out.append(
            {
                'title': f'{r.espacio.nombre} — {r.get_estado_display()}',
                'start': start.isoformat(),
                'end': end.isoformat(),
                'url': '',  # opcional: enlace a detalle si existe ruta pública
                'backgroundColor': colors.get(r.estado, '#0275d8'),
                'borderColor': colors.get(r.estado, '#0275d8'),
                'extendedProps': {
                    'espacio': r.espacio.nombre,
                    'usuario': r.usuario.get_nombre_completo(),
                    'estado': r.estado,
                },
            }
        )
    return out
