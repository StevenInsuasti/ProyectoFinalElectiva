"""
Vistas del módulo de Reservas.
Integrante 3 - Sistema de Reservas de Espacios

CRUD completo de reservas con:
  - Validación de conflictos
  - Control de estados (pendiente / aprobada / cancelada)
  - Historial por usuario
  - Confirmación automática o manual
  - Acceso diferenciado por rol
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.decorators import administrador_requerido
from espacios.models import Espacio, Horario
from .models import Reserva
from .forms import ReservaForm, ReservaAdminForm, CambiarEstadoForm, FiltroReservaForm


# ─── LISTA DE RESERVAS ────────────────────────────────────────────────────────

@login_required
def lista_reservas(request):
    """
    Lista de reservas con filtros.
    - Administrador: ve todas las reservas.
    - Usuario normal: ve solo sus propias reservas.
    """
    form_filtro = FiltroReservaForm(request.GET)

    if request.user.es_administrador:
        reservas = Reserva.objects.select_related(
            'usuario', 'espacio', 'horario'
        ).all()
    else:
        reservas = Reserva.objects.select_related(
            'usuario', 'espacio', 'horario'
        ).filter(usuario=request.user)

    # Aplicar filtros
    if form_filtro.is_valid():
        estado = form_filtro.cleaned_data.get('estado')
        fecha_desde = form_filtro.cleaned_data.get('fecha_desde')
        fecha_hasta = form_filtro.cleaned_data.get('fecha_hasta')
        espacio = form_filtro.cleaned_data.get('espacio')

        if estado:
            reservas = reservas.filter(estado=estado)
        if fecha_desde:
            reservas = reservas.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            reservas = reservas.filter(fecha__lte=fecha_hasta)
        if espacio:
            reservas = reservas.filter(espacio=espacio)

    # Estadísticas rápidas
    stats = {
        'total': reservas.count(),
        'pendientes': reservas.filter(estado=Reserva.ESTADO_PENDIENTE).count(),
        'aprobadas': reservas.filter(estado=Reserva.ESTADO_APROBADA).count(),
        'canceladas': reservas.filter(estado=Reserva.ESTADO_CANCELADA).count(),
    }

    context = {
        'reservas': reservas,
        'form_filtro': form_filtro,
        'stats': stats,
    }
    return render(request, 'reservas/lista_reservas.html', context)


# ─── DETALLE DE RESERVA ───────────────────────────────────────────────────────

@login_required
def detalle_reserva(request, pk):
    """
    Detalle de una reserva.
    El usuario solo puede ver sus propias reservas; el admin puede ver todas.
    """
    reserva = get_object_or_404(Reserva, pk=pk)

    # Control de acceso
    if not request.user.es_administrador and reserva.usuario != request.user:
        messages.error(request, 'No tienes permiso para ver esta reserva.')
        return redirect('reservas:lista_reservas')

    form_estado = CambiarEstadoForm()

    context = {
        'reserva': reserva,
        'form_estado': form_estado,
    }
    return render(request, 'reservas/detalle_reserva.html', context)


# ─── CREAR RESERVA ────────────────────────────────────────────────────────────

@login_required
def crear_reserva(request):
    """
    Crear una nueva reserva.
    Cualquier usuario autenticado puede crear reservas.
    """
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            try:
                reserva = form.save(commit=False)
                reserva.usuario = request.user
                # Confirmación automática según la configuración del espacio
                if reserva.espacio.confirmacion_automatica:
                    reserva.confirmacion_automatica = True
                reserva.save()
                if reserva.esta_aprobada:
                    messages.success(
                        request,
                        f'✅ Reserva creada y aprobada automáticamente para '
                        f'"{reserva.espacio.nombre}" el {reserva.fecha}.'
                    )
                else:
                    messages.success(
                        request,
                        f'✅ Reserva creada exitosamente para "{reserva.espacio.nombre}" '
                        f'el {reserva.fecha}. Estado: Pendiente de aprobación.'
                    )
                return redirect('reservas:detalle_reserva', pk=reserva.pk)
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            form.add_error(field if field in form.fields else None, error)
                messages.error(request, 'Por favor corrige los errores del formulario.')
            except Exception as e:
                messages.error(request, f'Error inesperado al crear la reserva: {e}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        # Pre-seleccionar espacio si viene por parámetro GET
        espacio_id = request.GET.get('espacio')
        initial = {}
        if espacio_id:
            try:
                espacio = Espacio.objects.get(pk=espacio_id, estado=Espacio.ESTADO_DISPONIBLE)
                initial['espacio'] = espacio
            except Espacio.DoesNotExist:
                pass
        form = ReservaForm(initial=initial)

    return render(request, 'reservas/form_reserva.html', {
        'form': form,
        'titulo': 'Nueva Reserva',
        'accion': 'Crear Reserva',
    })


# ─── EDITAR RESERVA ───────────────────────────────────────────────────────────

@login_required
def editar_reserva(request, pk):
    """
    Editar una reserva existente.
    - Usuario: solo puede editar sus propias reservas en estado pendiente.
    - Administrador: puede editar cualquier reserva.
    """
    reserva = get_object_or_404(Reserva, pk=pk)

    # Control de acceso
    if not request.user.es_administrador:
        if reserva.usuario != request.user:
            messages.error(request, 'No tienes permiso para editar esta reserva.')
            return redirect('reservas:lista_reservas')
        if not reserva.esta_pendiente:
            messages.warning(
                request,
                'Solo puedes editar reservas en estado pendiente. '
                f'Esta reserva está {reserva.get_estado_display().lower()}.'
            )
            return redirect('reservas:detalle_reserva', pk=pk)

    FormClass = ReservaAdminForm if request.user.es_administrador else ReservaForm

    if request.method == 'POST':
        form = FormClass(request.POST, instance=reserva)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Reserva actualizada correctamente.')
                return redirect('reservas:detalle_reserva', pk=reserva.pk)
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field if field in form.fields else None, error)
                messages.error(request, 'Por favor corrige los errores del formulario.')
            except Exception as e:
                messages.error(request, f'Error al actualizar la reserva: {e}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = FormClass(instance=reserva)

    return render(request, 'reservas/form_reserva.html', {
        'form': form,
        'reserva': reserva,
        'titulo': f'Editar Reserva #{reserva.pk}',
        'accion': 'Guardar cambios',
    })


# ─── CANCELAR RESERVA (usuario) ───────────────────────────────────────────────

@login_required
def cancelar_reserva(request, pk):
    """
    El usuario cancela su propia reserva (si es futura y no está ya cancelada).
    """
    reserva = get_object_or_404(Reserva, pk=pk)

    if not request.user.es_administrador and reserva.usuario != request.user:
        messages.error(request, 'No tienes permiso para cancelar esta reserva.')
        return redirect('reservas:lista_reservas')

    if not reserva.puede_cancelarse:
        messages.warning(
            request,
            'Esta reserva no puede cancelarse '
            '(ya está cancelada o es de una fecha pasada).'
        )
        return redirect('reservas:detalle_reserva', pk=pk)

    if request.method == 'POST':
        try:
            reserva.cancelar()
            messages.success(
                request,
                f'Reserva #{reserva.pk} cancelada correctamente.'
            )
            return redirect('reservas:lista_reservas')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al cancelar la reserva: {e}')

    return render(request, 'reservas/confirmar_cancelar.html', {'reserva': reserva})


# ─── ELIMINAR RESERVA (solo admin) ───────────────────────────────────────────

@login_required
@administrador_requerido
def eliminar_reserva(request, pk):
    """Eliminar permanentemente una reserva (solo administrador)."""
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.method == 'POST':
        reserva_str = str(reserva)
        reserva.delete()
        messages.success(request, f'Reserva eliminada: {reserva_str}')
        return redirect('reservas:lista_reservas')

    return render(request, 'reservas/confirmar_eliminar.html', {'reserva': reserva})


# ─── APROBAR / RECHAZAR (solo admin) ─────────────────────────────────────────

@login_required
@administrador_requerido
def cambiar_estado_reserva(request, pk):
    """
    El administrador aprueba o cancela una reserva con observaciones opcionales.
    """
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.method == 'POST':
        form = CambiarEstadoForm(request.POST)
        if form.is_valid():
            accion = form.cleaned_data['accion']
            observaciones = form.cleaned_data.get('observaciones', '')
            try:
                if accion == 'aprobar':
                    reserva.aprobar(observaciones=observaciones)
                    messages.success(
                        request,
                        f'✅ Reserva #{reserva.pk} aprobada correctamente.'
                    )
                elif accion == 'cancelar':
                    reserva.cancelar(observaciones=observaciones)
                    messages.success(
                        request,
                        f'Reserva #{reserva.pk} cancelada por el administrador.'
                    )
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error al cambiar el estado: {e}')
        else:
            messages.error(request, 'Formulario inválido.')

    return redirect('reservas:detalle_reserva', pk=pk)


# ─── HISTORIAL DEL USUARIO ────────────────────────────────────────────────────

@login_required
def historial_reservas(request):
    """
    Historial completo de reservas del usuario autenticado.
    Muestra todas las reservas pasadas y futuras con estadísticas.
    """
    reservas = Reserva.objects.filter(
        usuario=request.user
    ).select_related('espacio', 'horario').order_by('-fecha', '-fecha_creacion')

    hoy = timezone.localdate()
    futuras = reservas.filter(fecha__gte=hoy).exclude(estado=Reserva.ESTADO_CANCELADA)
    pasadas = reservas.filter(fecha__lt=hoy)

    stats = {
        'total': reservas.count(),
        'pendientes': reservas.filter(estado=Reserva.ESTADO_PENDIENTE).count(),
        'aprobadas': reservas.filter(estado=Reserva.ESTADO_APROBADA).count(),
        'canceladas': reservas.filter(estado=Reserva.ESTADO_CANCELADA).count(),
        'futuras': futuras.count(),
    }

    context = {
        'reservas': reservas,
        'futuras': futuras,
        'pasadas': pasadas,
        'stats': stats,
        'hoy': hoy,
    }
    return render(request, 'reservas/historial_reservas.html', context)


# ─── PANEL ADMIN DE RESERVAS ─────────────────────────────────────────────────

@login_required
@administrador_requerido
def panel_admin_reservas(request):
    """
    Panel de administración de reservas: vista global con estadísticas.
    Compatible con integración futura del dashboard.
    """
    hoy = timezone.localdate()
    reservas_hoy = Reserva.objects.filter(fecha=hoy).select_related(
        'usuario', 'espacio', 'horario'
    )
    pendientes = Reserva.objects.filter(
        estado=Reserva.ESTADO_PENDIENTE
    ).select_related('usuario', 'espacio', 'horario').order_by('fecha')

    stats = {
        'total': Reserva.objects.count(),
        'pendientes': Reserva.objects.filter(estado=Reserva.ESTADO_PENDIENTE).count(),
        'aprobadas': Reserva.objects.filter(estado=Reserva.ESTADO_APROBADA).count(),
        'canceladas': Reserva.objects.filter(estado=Reserva.ESTADO_CANCELADA).count(),
        'hoy': reservas_hoy.count(),
    }

    context = {
        'reservas_hoy': reservas_hoy,
        'pendientes': pendientes,
        'stats': stats,
        'hoy': hoy,
    }
    return render(request, 'reservas/panel_admin.html', context)


# ─── API JSON ─────────────────────────────────────────────────────────────────

@login_required
def api_horarios_disponibles(request, espacio_pk):
    """
    Endpoint JSON: devuelve los horarios activos de un espacio
    con indicación de disponibilidad para una fecha dada.
    Parámetro GET: ?fecha=YYYY-MM-DD
    """
    espacio = get_object_or_404(Espacio, pk=espacio_pk)
    fecha_str = request.GET.get('fecha')
    horarios = Horario.objects.filter(espacio=espacio, activo=True)

    data = []
    for h in horarios:
        disponible = True
        if fecha_str:
            try:
                from datetime import date
                fecha = date.fromisoformat(fecha_str)
                # Verificar si el día coincide
                if fecha.weekday() != h.dia_semana:
                    continue  # No aplica para ese día
                # Verificar conflictos
                conflicto = Reserva.objects.filter(
                    espacio=espacio,
                    horario=h,
                    fecha=fecha,
                ).exclude(estado=Reserva.ESTADO_CANCELADA).exists()
                disponible = not conflicto
            except ValueError:
                pass

        data.append({
            'id': h.id,
            'dia': h.get_dia_semana_display(),
            'hora_inicio': h.hora_inicio.strftime('%H:%M'),
            'hora_fin': h.hora_fin.strftime('%H:%M'),
            'disponible': disponible,
        })

    return JsonResponse({
        'espacio': espacio.nombre,
        'horarios': data,
    })
