from miapp.forms import UsuarioRegistroForm
from django.shortcuts import redirect, render
from django.contrib import messages
from miapp.forms import LoginForm
from miapp.models import Usuario

# Create your views here.
def index(request):
    # return HttpResponse ("Hola Mundo.")
    return render(request, "home/index.html")

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
                #messages.success(request, f"¡Bienvenido de nuevo, {usuario.nombre}!")
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
            # El formulario mostrará los errores automáticamente
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = UsuarioRegistroForm()

    return render(request, "home/registrar.html", {"form": form})
