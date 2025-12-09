from miapp.forms import UsuarioRegistroForm
from django.shortcuts import redirect, render
from django.contrib import messages
from miapp.forms import LoginForm
from miapp.models import Usuario, Tarea
from django.utils import timezone
from datetime import timedelta

# Create your views here.
def index(request):
    # Verificar que el usuario esté logueado
    if "usuario_id" not in request.session:
        messages.error(request, "Debes iniciar sesión para ver tus tareas.")
        return redirect("login")

    # Obtener el ID del usuario logueado
    usuario_id = request.session["usuario_id"]
    
    usuario_actual = Usuario.objects.get(id=usuario_id)

    # Obtener fechas
    hoy = timezone.now().date()
    manana = hoy + timedelta(days=1)
    fin_semana = hoy + timedelta(days=7)

    # Tareas para hoy (que vencen hoy y no están completadas)
    tareas_hoy = Tarea.objects.filter(
        usuario_id=usuario_id,
        fecha_entrega=hoy,
        estatus__nombre__in=["nue", "pro"]
    ).count()

    # Tareas para esta semana (excluyendo hoy)
    tareas_semana = Tarea.objects.filter(
        usuario_id=usuario_id,
        fecha_entrega__range=[manana, fin_semana],
        estatus__nombre__in=["nue", "pro"]
    ).count()

    # Tareas que ya vencieron (fecha anterior a hoy y no completadas)
    tareas_vencidas = Tarea.objects.filter(
        usuario_id=usuario_id,
        fecha_entrega__lt=hoy,
        estatus__nombre__in=["nue", "pro"]
    ).count()

    context = {
        "usuario_actual": usuario_actual,
        "tareas_por_vencer": {
            "hoy": tareas_hoy,
            "proxima_semana": tareas_semana,
            "vencidas": tareas_vencidas
        }
    }
    return render(request, "home/index.html", context)

def login(request):
    # Si ya hay un usuario en sesión, redirigir al inicio
    if "usuario_id" in request.session:
        return redirect("index")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data["correo"]
            contrasenia = form.cleaned_data["contrasenia"]

            # Verificar credenciales en la base de datos
            try:
                usuario = Usuario.objects.get(correo=correo, contrasenia=contrasenia)
                # Guardar usuario en sesión
                request.session["usuario_id"] = usuario.id
                request.session["usuario_nombre"] = usuario.nombre_completo
                request.session["usuario_email"] = usuario.correo
                messages.success(request, f"¡Bienvenido de nuevo, {usuario.nombre}!")
                return redirect("index")

            except Usuario.DoesNotExist:
                # Credenciales incorrectas
                form.add_error(None, "Correo electrónico o contraseña incorrectos")
                messages.error(
                    request, "Credenciales incorrectas. Por favor, intenta de nuevo."
                )
    else:
        form = LoginForm()

    return render(request, "home/login.html", {"form": form})


def logout(request):
    # Cerrar sesión
    if "usuario_id" in request.session:
        del request.session["usuario_id"]
        del request.session["usuario_nombre"]
        del request.session["usuario_email"]

    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("login")


def registrar(request):
    if request.method == "POST":
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            # Guardar el usuario
            usuario = form.save()
            messages.success(
                request, "¡Cuenta creada exitosamente! Ahora puedes iniciar sesión."
            )
            return redirect("login")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = UsuarioRegistroForm()

    return render(request, "home/registrar.html", {"form": form})
