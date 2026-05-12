"""
Vistas del módulo de Gestión de Espacios y Horarios.
Integrante 2 - Sistema de Reservas de Espacios
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse

from accounts.decorators import administrador_requerido
from .models import Espacio, Horario
from .forms import EspacioForm, HorarioForm, FiltroEspacioForm


# ─── ESPACIOS ────────────────────────────────────────────────────────────────

@login_required
def lista_espacios(request):
    """Lista todos los espacios con filtros de búsqueda."""
    form_filtro = FiltroEspacioForm(request.GET)
    espacios = Espacio.objects.annotate(total_horarios=Count('horarios'))

    if form_filtro.is_valid():
        buscar = form_filtro.cleaned_data.get('buscar')
        tipo = form_filtro.cleaned_data.get('tipo')
        estado = form_filtro.cleaned_data.get('estado')

        if buscar:
            espacios = espacios.filter(
                Q(nombre__icontains=buscar) | Q(ubicacion__icontains=buscar)
            )
        if tipo:
            espacios = espacios.filter(tipo=tipo)
        if estado:
            espacios = espacios.filter(estado=estado)

    context = {
        'espacios': espacios,
        'form_filtro': form_filtro,
        'total': espacios.count(),
    }
    return render(request, 'espacios/lista_espacios.html', context)


@login_required
def detalle_espacio(request, pk):
    """Detalle de un espacio con sus horarios."""
    espacio = get_object_or_404(Espacio, pk=pk)
    horarios = espacio.horarios.all().order_by('dia_semana', 'hora_inicio')
    context = {
        'espacio': espacio,
        'horarios': horarios,
    }
    return render(request, 'espacios/detalle_espacio.html', context)


@login_required
@administrador_requerido
def crear_espacio(request):
    """Crear un nuevo espacio (solo administrador)."""
    if request.method == 'POST':
        form = EspacioForm(request.POST)
        if form.is_valid():
            espacio = form.save()
            messages.success(request, f'Espacio "{espacio.nombre}" creado exitosamente.')
            return redirect('espacios:detalle_espacio', pk=espacio.pk)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = EspacioForm()

    return render(request, 'espacios/form_espacio.html', {
        'form': form,
        'titulo': 'Crear Espacio',
        'accion': 'Crear',
    })


@login_required
@administrador_requerido
def editar_espacio(request, pk):
    """Editar un espacio existente (solo administrador)."""
    espacio = get_object_or_404(Espacio, pk=pk)
    if request.method == 'POST':
        form = EspacioForm(request.POST, instance=espacio)
        if form.is_valid():
            form.save()
            messages.success(request, f'Espacio "{espacio.nombre}" actualizado correctamente.')
            return redirect('espacios:detalle_espacio', pk=espacio.pk)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = EspacioForm(instance=espacio)

    return render(request, 'espacios/form_espacio.html', {
        'form': form,
        'espacio': espacio,
        'titulo': f'Editar: {espacio.nombre}',
        'accion': 'Guardar cambios',
    })


@login_required
@administrador_requerido
def eliminar_espacio(request, pk):
    """Eliminar un espacio (solo administrador, requiere confirmación POST)."""
    espacio = get_object_or_404(Espacio, pk=pk)
    if request.method == 'POST':
        nombre = espacio.nombre
        espacio.delete()
        messages.success(request, f'Espacio "{nombre}" eliminado correctamente.')
        return redirect('espacios:lista_espacios')
    return render(request, 'espacios/confirmar_eliminar.html', {
        'objeto': espacio,
        'tipo': 'espacio',
        'cancelar_url': 'espacios:detalle_espacio',
        'cancelar_pk': espacio.pk,
    })


# ─── HORARIOS ────────────────────────────────────────────────────────────────

@login_required
def lista_horarios(request):
    """Lista todos los horarios con filtro por espacio."""
    espacio_id = request.GET.get('espacio')
    horarios = Horario.objects.select_related('espacio').order_by(
        'espacio__nombre', 'dia_semana', 'hora_inicio'
    )
    espacios = Espacio.objects.all().order_by('nombre')

    if espacio_id:
        horarios = horarios.filter(espacio_id=espacio_id)

    context = {
        'horarios': horarios,
        'espacios': espacios,
        'espacio_seleccionado': espacio_id,
    }
    return render(request, 'espacios/lista_horarios.html', context)


@login_required
@administrador_requerido
def crear_horario(request, espacio_pk=None):
    """Crear un horario, opcionalmente asociado a un espacio."""
    espacio = get_object_or_404(Espacio, pk=espacio_pk) if espacio_pk else None

    if request.method == 'POST':
        form = HorarioForm(request.POST, espacio=espacio)
        if form.is_valid():
            try:
                horario = form.save()
                messages.success(
                    request,
                    f'Horario creado: {horario.get_dia_semana_display()} '
                    f'{horario.hora_inicio.strftime("%H:%M")} - {horario.hora_fin.strftime("%H:%M")}'
                )
                return redirect('espacios:detalle_espacio', pk=horario.espacio.pk)
            except Exception as e:
                messages.error(request, f'Error al guardar: {e}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = HorarioForm(espacio=espacio)

    return render(request, 'espacios/form_horario.html', {
        'form': form,
        'espacio': espacio,
        'titulo': 'Agregar Horario',
        'accion': 'Crear',
    })


@login_required
@administrador_requerido
def editar_horario(request, pk):
    """Editar un horario existente."""
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        form = HorarioForm(request.POST, instance=horario)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Horario actualizado correctamente.')
                return redirect('espacios:detalle_espacio', pk=horario.espacio.pk)
            except Exception as e:
                messages.error(request, f'Error al guardar: {e}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = HorarioForm(instance=horario)

    return render(request, 'espacios/form_horario.html', {
        'form': form,
        'horario': horario,
        'espacio': horario.espacio,
        'titulo': 'Editar Horario',
        'accion': 'Guardar cambios',
    })


@login_required
@administrador_requerido
def eliminar_horario(request, pk):
    """Eliminar un horario (requiere confirmación POST)."""
    horario = get_object_or_404(Horario, pk=pk)
    espacio_pk = horario.espacio.pk
    if request.method == 'POST':
        horario.delete()
        messages.success(request, 'Horario eliminado correctamente.')
        return redirect('espacios:detalle_espacio', pk=espacio_pk)
    return render(request, 'espacios/confirmar_eliminar.html', {
        'objeto': horario,
        'tipo': 'horario',
        'cancelar_url': 'espacios:detalle_espacio',
        'cancelar_pk': espacio_pk,
    })


# ─── API JSON (para integración con reservas / calendario) ───────────────────

@login_required
def api_horarios_espacio(request, espacio_pk):
    """
    Endpoint JSON: devuelve los horarios activos de un espacio.
    Preparado para que el módulo de Reservas (Integrante 3) lo consuma.
    """
    espacio = get_object_or_404(Espacio, pk=espacio_pk)
    horarios = espacio.horarios.filter(activo=True).values(
        'id', 'dia_semana', 'hora_inicio', 'hora_fin'
    )
    data = [
        {
            'id': h['id'],
            'dia': h['dia_semana'],
            'hora_inicio': h['hora_inicio'].strftime('%H:%M'),
            'hora_fin': h['hora_fin'].strftime('%H:%M'),
        }
        for h in horarios
    ]
    return JsonResponse({'espacio': espacio.nombre, 'horarios': data})


@login_required
def api_espacios_disponibles(request):
    """
    Endpoint JSON: devuelve espacios disponibles.
    Preparado para el módulo de Reservas (Integrante 3).
    """
    espacios = Espacio.objects.filter(estado=Espacio.ESTADO_DISPONIBLE).values(
        'id', 'nombre', 'tipo', 'capacidad', 'ubicacion'
    )
    return JsonResponse({'espacios': list(espacios)})
