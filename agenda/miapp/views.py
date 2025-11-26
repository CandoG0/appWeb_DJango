from datetime import timedelta
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils import timezone
from .forms import TareaForm
from .models import Tarea, Estatu, Usuario

# from miapp.forms import CarreraForm, EstudianteForm
# from miapp.models import Carrera, Estudiante
# Create your views here.


# Cargar vista para el formulario de tareas
def crear_tarea(request):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para crear tareas.")
        return redirect("login")

    # Asegurar que existan los estatus
    crear_estatus_inicial()

    if request.method == "POST":
        print("Formulario enviado por POST")
        print("Datos recibidos:", request.POST)

        # Usar el formulario de Django con los datos POST
        form = TareaForm(request.POST)

        if form.is_valid():
            print("Formulario válido")
            try:
                # Crear la tarea pero no guardar aún
                tarea = form.save(commit=False)

                # Asignar el usuario logueado
                usuario = Usuario.objects.get(id=request.session["usuario_id"])
                tarea.usuario = usuario
                print(f"Usuario asignado: {usuario.nombre_completo}")

                # Asignar estatus "Nuevo" por defecto
                estatus_nuevo = Estatu.objects.get(nombre="nue")
                tarea.estatus = estatus_nuevo
                print("Estatus asignado: Nuevo")

                # Guardar la tarea en la base de datos
                tarea.save()
                print(f"Tarea guardada con ID: {tarea.id}")

                messages.success(
                    request, f'¡Tarea "{tarea.nombre_tarea}" creada exitosamente!'
                )
                return redirect(
                    "miapp:listar_tareas"
                )  # Cambia por tu URL de lista de tareas

            except Usuario.DoesNotExist:
                print("Error: Usuario no encontrado")
                messages.error(request, "Usuario no encontrado.")
            except Estatu.DoesNotExist:
                print("Error: Estatus no encontrado")
                messages.error(request, "Error en la configuración del sistema.")
            except Exception as e:
                print(f"Error inesperado: {e}")
                messages.error(request, f"Error al crear la tarea: {e}")
        else:
            print("Formulario inválido. Errores:", form.errors)
            messages.error(request, "Por favor corrige los errores en el formulario.")

    else:
        # Método GET - mostrar formulario vacío
        print("Mostrando formulario vacío (GET)")
        form = TareaForm()

    context = {
        "form": form,
        "today": timezone.now().strftime("%Y-%m-%d"),  # Para el campo date
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
    print("📋 Estatus iniciales verificados/creados")


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

    # Podemos establecer un límite opcional, por ejemplo 30 días en el futuro
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


def detalle_tarea(request):
    return render(request, "miapp/detalle_tarea.html")


def calendario(request):
    return render(request, "miapp/calendario.html")
