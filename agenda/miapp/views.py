from datetime import timedelta
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .forms import TareaForm
from .models import Tarea, Estatu, Usuario, ComentarioTarea
import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET

# Create your views here.


# Cargar vista para el formulario de tareas
def crear_tarea(request):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para crear tareas.")
        return redirect("login")

    if request.method == "POST":
        form = TareaForm(request.POST)

        if form.is_valid():
            try:
                # Crear la tarea pero no guardar aún
                tarea = form.save(commit=False)

                # Asignar el usuario logueado
                usuario = Usuario.objects.get(id=request.session["usuario_id"])
                tarea.usuario = usuario

                # Asignar estatus "Nuevo" por defecto
                estatus_nuevo = Estatu.objects.get(nombre="nue")
                tarea.estatus = estatus_nuevo

                # Guardar la tarea
                tarea.save()

                messages.success(
                    request, f'¡Tarea "{tarea.nombre_tarea}" creada exitosamente!'
                )
                return redirect("miapp:listar_tareas")

            except Exception as e:
                messages.error(request, f"Error al crear la tarea: {e}")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Método GET - mostrar formulario vacío
        form = TareaForm()

    context = {
        "form": form,
        "today": timezone.now().strftime("%Y-%m-%d"),
        "modo": "crear",
    }
    return render(request, "miapp/crear_tarea.html", context)


def crear_estatus_inicial():
    """Crea los estatus iniciales si no existen"""
    estatus_data = [
        {"nombre": "nue"},  # Nuevo
        {"nombre": "pro"},  # En proceso
        {"nombre": "fin"},  # Finalizado
    ]

    for data in estatus_data:
        Estatu.objects.get_or_create(**data)
    print("Estatus iniciales verificados/creados")


def listar_tareas(request):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para ver tus tareas.")
        return redirect("login")

    # Obtener el ID del usuario logueado
    usuario_id = request.session["usuario_id"]

    # Filtrar tareas del usuario actual, ordenadas por fecha de entrega
    tareas = Tarea.objects.filter(usuario_id=usuario_id).order_by(
        "fecha_entrega", "prioridad"
    )

    # Contadores para estadísticas
    total_tareas = tareas.count()
    tareas_pendientes = tareas.filter(estatus__nombre="nue").count()
    tareas_en_proceso = tareas.filter(estatus__nombre="pro").count()
    tareas_completadas = tareas.filter(estatus__nombre="fin").count()

    context = {
        "tareas": tareas,
        "total_tareas": total_tareas,
        "tareas_pendientes": tareas_pendientes,
        "tareas_en_proceso": tareas_en_proceso,
        "tareas_completadas": tareas_completadas,
    }

    return render(request, "miapp/lista_tareas.html", context)


def tareas_vencer(request):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para ver tus tareas.")
        return redirect("login")

    # Obtener el ID del usuario logueado
    usuario_id = request.session["usuario_id"]

    # Obtener fechas de hoy y mañana
    hoy = timezone.now().date()
    manana = hoy + timedelta(days=1)

    # Filtrar tareas del usuario actual que vencen hoy o mañana
    # y que no estén completadas
    tareas = Tarea.objects.filter(
        usuario_id=usuario_id,
        fecha_entrega__range=[hoy, manana],
        estatus__nombre__in=["nue", "pro"],  # Solo tareas no completadas
    ).order_by("fecha_entrega", "prioridad")

    # Contar tareas por vencer
    tareas_hoy = tareas.filter(fecha_entrega=hoy).count()
    tareas_manana = tareas.filter(fecha_entrega=manana).count()

    context = {
        "tareas": tareas,
        "tareas_hoy": tareas_hoy,
        "tareas_manana": tareas_manana,
        "hoy": hoy,
        "manana": manana,
    }

    return render(request, "miapp/tareas_vencer.html", context)


def tareas_pendientes(request):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para ver tus tareas.")
        return redirect("login")

    # Obtener el ID del usuario logueado
    usuario_id = request.session["usuario_id"]

    # Obtener fechas: desde 3 días en adelante (excluyendo hoy y mañana)
    hoy = timezone.now().date()
    fecha_inicio = hoy + timedelta(days=3)

    # Establecer un límite opcional, por ejemplo 30 días en el futuro
    fecha_fin = hoy + timedelta(days=30)

    # Filtrar tareas del usuario actual que vencen en 3 días o más
    # y que no estén completadas
    tareas = Tarea.objects.filter(
        usuario_id=usuario_id,
        fecha_entrega__range=[fecha_inicio, fecha_fin],
        estatus__nombre__in=["nue", "pro"],  # Solo tareas no completadas
    ).order_by("fecha_entrega", "prioridad")

    # Contar tareas por rango de días
    tareas_3_7_dias = tareas.filter(
        fecha_entrega__range=[fecha_inicio, hoy + timedelta(days=7)]
    ).count()

    tareas_8_15_dias = tareas.filter(
        fecha_entrega__range=[hoy + timedelta(days=8), hoy + timedelta(days=15)]
    ).count()

    tareas_mas_15_dias = tareas.filter(
        fecha_entrega__gte=hoy + timedelta(days=16)
    ).count()

    context = {
        "tareas": tareas,
        "tareas_3_7_dias": tareas_3_7_dias,
        "tareas_8_15_dias": tareas_8_15_dias,
        "tareas_mas_15_dias": tareas_mas_15_dias,
        "total_tareas": tareas.count(),
        "hoy": hoy,
    }

    return render(request, "miapp/tareas_pendientes.html", context)


def tareas_completadas(request):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para ver tus tareas.")
        return redirect("login")

    # Obtener el ID del usuario logueado
    usuario_id = request.session["usuario_id"]

    # Filtrar tareas del usuario actual que están completadas
    tareas = Tarea.objects.filter(
        usuario_id=usuario_id, estatus__nombre="fin"  # Solo tareas completadas
    ).order_by(
        "-fecha_entrega"
    )  # Ordenar por fecha más reciente primero

    # Estadísticas de tareas completadas
    total_completadas = tareas.count()

    # Tareas completadas esta semana
    inicio_semana = timezone.now().date() - timedelta(days=7)
    completadas_semana = tareas.filter(fecha_entrega__gte=inicio_semana).count()

    # Tareas completadas a tiempo vs vencidas
    completadas_a_tiempo = tareas.filter(
        fecha_entrega__gte=timezone.now().date()
    ).count()

    completadas_vencidas = total_completadas - completadas_a_tiempo

    context = {
        "tareas": tareas,
        "total_completadas": total_completadas,
        "completadas_semana": completadas_semana,
        "completadas_a_tiempo": completadas_a_tiempo,
        "completadas_vencidas": completadas_vencidas,
    }

    return render(request, "miapp/tareas_completadas.html", context)


def marcar_completada(request, tarea_id):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para realizar esta acción.")
        return redirect("login")

    try:
        # Obtener la tarea y verificar que pertenece al usuario
        tarea = Tarea.objects.get(id=tarea_id, usuario_id=request.session["usuario_id"])

        # Obtener el estatus "Completado"
        estatus_completado = Estatu.objects.get(nombre="fin")

        # Cambiar el estatus a completado
        tarea.estatus = estatus_completado
        tarea.save()

        messages.success(
            request, f'¡Tarea "{tarea.nombre_tarea}" marcada como completada!'
        )

    except Tarea.DoesNotExist:
        messages.error(
            request, "La tarea no existe o no tienes permisos para modificarla."
        )
    except Estatu.DoesNotExist:
        messages.error(request, "Error en la configuración del sistema.")
    except Exception as e:
        messages.error(request, f"Error al marcar la tarea como completada: {e}")

    # Redirigir a la página desde donde vino el usuario
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    else:
        return redirect("miapp:listar_tareas")


def detalle_tarea(request, tarea_id):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        print("DEBUG: Usuario no logueado, redirigiendo a login")
        messages.error(
            request, "Debes iniciar sesión para ver los detalles de la tarea."
        )
        return redirect("login")

    try:
        # Obtener el ID del usuario logueado
        usuario_id = request.session["usuario_id"]

        # Obtener la tarea
        tarea = Tarea.objects.get(id=tarea_id)

        # Verificar que la tarea pertenezca al usuario
        if tarea.usuario_id != usuario_id:
            messages.error(request, "No tienes permisos para ver esta tarea.")
            return redirect("miapp:listar_tareas")

        # Calcular días restantes
        hoy = timezone.now().date()
        dias_restantes = (tarea.fecha_entrega - hoy).days

        context = {
            "tarea": tarea,
            "dias_restantes": dias_restantes,
            "hoy": hoy,
        }

        return render(request, "miapp/detalle_tarea.html", context)

    except Tarea.DoesNotExist:
        messages.error(request, "La tarea no existe.")
        return redirect("miapp:listar_tareas")
    except Exception as e:
        print(f"DEBUG: ERROR inesperado: {str(e)}")
        messages.error(request, f"Error al cargar la tarea: {str(e)}")
        return redirect("miapp:listar_tareas")


def editar_tarea(request, tarea_id):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para editar tareas.")
        return redirect("login")

    usuario_id = request.session["usuario_id"]

    try:
        # Obtener la tarea y verificar que pertenece al usuario
        tarea = Tarea.objects.get(id=tarea_id, usuario_id=usuario_id)

        if request.method == "POST":
            # Usar el formulario con los datos POST y la instancia de la tarea
            form = TareaForm(request.POST, instance=tarea)

            if form.is_valid():
                # Guardar los cambios
                tarea_editada = form.save(commit=False)
                tarea_editada.usuario_id = usuario_id  # Mantener el usuario
                tarea_editada.save()

                messages.success(
                    request,
                    f'¡Tarea "{tarea_editada.nombre_tarea}" actualizada exitosamente!',
                )
                return redirect("miapp:detalle_tarea", tarea_id=tarea_id)
            else:
                messages.error(
                    request, "Por favor corrige los errores en el formulario."
                )
        else:
            # Método GET - mostrar formulario con datos actuales
            form = TareaForm(instance=tarea)

        # Preparar el contexto para el template
        context = {
            "form": form,
            "tarea": tarea,
            "today": timezone.now().strftime("%Y-%m-d"),
            "modo": "editar",
        }

        # Usar el mismo template que crear_tarea
        return render(request, "miapp/crear_tarea.html", context)

    except Tarea.DoesNotExist:
        messages.error(
            request, "La tarea no existe o no tienes permisos para editarla."
        )
        return redirect("miapp:listar_tareas")
    except Exception as e:
        messages.error(request, f"Error al editar la tarea: {e}")
        return redirect("miapp:listar_tareas")


def eliminar_tarea(request, tarea_id):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para realizar esta acción.")
        return redirect("login")

    usuario_id = request.session["usuario_id"]

    if request.method == "POST":
        try:
            # Obtener la tarea y verificar que pertenece al usuario
            tarea = get_object_or_404(Tarea, id=tarea_id, usuario_id=usuario_id)

            # Guardar el nombre para el mensaje
            nombre_tarea = tarea.nombre_tarea

            # Eliminar la tarea
            tarea.delete()

            messages.success(request, f'Tarea "{nombre_tarea}" eliminada exitosamente.')
            return redirect("miapp:listar_tareas")

        except Exception as e:
            messages.error(request, f"Error al eliminar la tarea: {str(e)}")
            return redirect("miapp:detalle_tarea", tarea_id=tarea_id)

    # Si no es POST, redirigir al detalle
    return redirect("miapp:detalle_tarea", tarea_id=tarea_id)


def actualizar_estado(request, tarea_id):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para realizar esta acción.")
        return redirect("login")

    usuario_id = request.session["usuario_id"]

    if request.method == "POST":
        try:
            # Obtener la tarea y verificar que pertenece al usuario
            tarea = get_object_or_404(Tarea, id=tarea_id, usuario_id=usuario_id)
            usuario = get_object_or_404(Usuario, id=usuario_id)

            # Obtener el nuevo estado del formulario
            nuevo_estado_nombre = request.POST.get("estado")
            comentario = request.POST.get("comentario", "").strip()

            if not nuevo_estado_nombre:
                messages.error(request, "Debes seleccionar un estado.")
                return redirect("miapp:detalle_tarea", tarea_id=tarea_id)

            # Buscar el objeto Estatu correspondiente
            nuevo_estado = get_object_or_404(Estatu, nombre=nuevo_estado_nombre)

            # Guardar el estado anterior para el mensaje
            estado_anterior = tarea.estatus.nombre

            # Actualizar el estado
            tarea.estatus = nuevo_estado
            tarea.save()

            # GUARDAR COMENTARIO SI EXISTE - ¡CORREGIDO!
            if (
                comentario
            ): 
                ComentarioTarea.objects.create(
                    tarea=tarea,
                    usuario=usuario,
                    contenido=comentario,
                    tipo="seg",  # 'seg' para seguimiento (cambio de estado)
                )

                # Mensaje con comentario
                messages.success(request, f"Estado actualizado y comentario agregado.")
            else:
                # Mensaje sin comentario
                messages.success(request, f"Estado actualizado correctamente.")

            # Mensaje adicional según el cambio de estado
            if estado_anterior != nuevo_estado_nombre:
                if nuevo_estado_nombre == "fin":
                    messages.success(
                        request,
                        f'¡Tarea "{tarea.nombre_tarea}" marcada como completada!',
                    )
                elif nuevo_estado_nombre == "pro":
                    messages.info(
                        request, f'Tarea "{tarea.nombre_tarea}" ahora está en progreso.'
                    )
                else:
                    messages.info(request, f"Estado de la tarea actualizado.")
            else:
                messages.info(
                    request,
                    f'El estado de la tarea ya estaba como "{nuevo_estado_nombre}".',
                )

        except Exception as e:
            messages.error(request, f"Error al actualizar el estado: {str(e)}")
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error actualizando estado tarea {tarea_id}: {str(e)}")

    # Redirigir de vuelta al detalle de la tarea
    return redirect("miapp:detalle_tarea", tarea_id=tarea_id)


def calendario_view(request):
    """Vista principal del calendario"""
    # Obtener tareas del usuario actual
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        # Redirigir a login si no está autenticado
        return redirect("login")

    return render(request, "miapp/calendario.html", {})


@require_GET
def tareas_calendario_api(request):
    """API para obtener tareas en formato JSON para el calendario"""
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return JsonResponse([], safe=False)

    try:
        # Obtener usuario
        usuario = Usuario.objects.get(id=usuario_id)

        # Obtener tareas del usuario con fecha de entrega
        tareas = Tarea.objects.filter(
            usuario=usuario, fecha_entrega__isnull=False
        ).select_related(
            "estatus"
        ) 

        # Convertir a formato FullCalendar
        eventos = []
        for tarea in tareas:
            # Obtener información del estado
            estado_nombre = ""
            estado_display = ""

            if tarea.estatus:
                estado_nombre = tarea.estatus.nombre  # 'nue', 'pro', 'fin'
                # Usar get_nombre_display() si existe, sino el nombre
                if hasattr(tarea.estatus, "get_nombre_display"):
                    estado_display = tarea.estatus.get_nombre_display()
                else:
                    estado_display = estado_nombre.upper()

            # Determinar color según estado
            color = "#895159"  # Color por defecto (SECONDARY MAROON)

            if estado_nombre == "fin":
                color = "#6A3F46"  # Completado
            elif estado_nombre == "pro":
                color = "#E6B8A8"  # En progreso (PEACH)
            elif estado_nombre == "nue":
                color = "#D5D8F0"  # Nuevo (PERIWINKLE variante)

            # Determinar si está vencida
            hoy = datetime.now().date()
            if tarea.fecha_entrega < hoy and estado_nombre != "fin":
                color = "#C44545"  # Vencida

            # Obtener display names usando los métodos del modelo
            modalidad_display = (
                tarea.get_modalidad_display()
                if hasattr(tarea, "get_modalidad_display")
                else "Individual"
            )
            prioridad_display = (
                tarea.get_prioridad_display()
                if hasattr(tarea, "get_prioridad_display")
                else "Media"
            )

            evento = {
                "id": tarea.id,
                "title": tarea.nombre_tarea,
                "start": tarea.fecha_entrega.isoformat(),
                "color": color,
                "textColor": (
                    "#FFFFFF"
                    if color in ["#895159", "#6A3F46", "#C44545"]
                    else "#000000"
                ),
                "extendedProps": {
                    "asignatura": tarea.asignatura,
                    "descripcion": tarea.descripcion_tarea or "",
                    "estado": estado_nombre,
                    "estado_display": estado_display,
                    "modalidad": modalidad_display,
                    "prioridad": prioridad_display,
                    "fecha_creacion": (
                        tarea.fecha_creacion.isoformat()
                        if tarea.fecha_creacion
                        else None
                    ),
                    "usuario": (
                        usuario.nombre_completo
                        if hasattr(usuario, "nombre_completo")
                        else usuario.nombre_usuario
                    ),
                },
            }
            eventos.append(evento)

        return JsonResponse(eventos, safe=False)

    except Usuario.DoesNotExist:
        return JsonResponse([], safe=False)
    except Exception as e:
        print(f"Error en API de calendario: {str(e)}")
        import traceback

        traceback.print_exc()  # Para ver el traceback completo

        hoy = datetime.now().date()
        eventos_debug = [
            {
                "id": 999,
                "title": "Tarea de ejemplo (Debug)",
                "start": hoy.isoformat(),
                "color": "#895159",
                "textColor": "#FFFFFF",
                "extendedProps": {
                    "asignatura": "Debug",
                    "descripcion": f"Error: {str(e)[:50]}...",
                    "estado": "nue",
                    "estado_display": "NUEVO",
                    "modalidad": "Individual",
                    "prioridad": "Alta",
                },
            },
            {
                "id": 998,
                "title": "Tarea mañana",
                "start": (hoy + timedelta(days=1)).isoformat(),
                "color": "#E6B8A8",
                "textColor": "#895159",
                "extendedProps": {
                    "asignatura": "Programación",
                    "descripcion": "Tarea en progreso",
                    "estado": "pro",
                    "estado_display": "EN PROGRESO",
                    "modalidad": "En Equipo",
                    "prioridad": "Media",
                },
            },
        ]
        return JsonResponse(eventos_debug, safe=False)
