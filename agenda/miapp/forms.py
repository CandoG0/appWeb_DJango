from django import forms
from .models import Usuario, Tarea
from django.core.exceptions import ValidationError
from django.utils import timezone

# Formularios que se utilizan para enviar registros a la base de datos
# Cada formulario puede tener una que otra funcion de utilidad
class UsuarioRegistroForm(forms.ModelForm):
    confirmar_contrasenia = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Repite tu contraseña"}
        ),
        label="Confirmar Contraseña",
    )

    class Meta:
        model = Usuario
        fields = [
            "nombre",
            "appat",
            "apmat",
            "nombre_usuario",
            "fecha_nacimiento",
            "correo",
            "contrasenia",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Tu nombre"}
            ),
            "appat": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Apellido paterno"}
            ),
            "apmat": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Apellido materno"}
            ),
            "nombre_usuario": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de usuario único",
                }
            ),
            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "correo": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "tu@correo.com"}
            ),
            "contrasenia": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Crea una contraseña segura",
                }
            ),
        }
        labels = {
            "nombre": "Nombre",
            "appat": "Apellido Paterno",
            "apmat": "Apellido Materno",
            "nombre_usuario": "Nombre de Usuario",
            "fecha_nacimiento": "Fecha de Nacimiento",
            "correo": "Correo Electrónico",
            "contrasenia": "Contraseña",
        }

    def clean(self):
        cleaned_data = super().clean()
        contrasenia = cleaned_data.get("contrasenia")
        confirmar_contrasenia = cleaned_data.get("confirmar_contrasenia")

        if (
            contrasenia
            and confirmar_contrasenia
            and contrasenia != confirmar_contrasenia
        ):
            raise ValidationError("Las contraseñas no coinciden")

        return cleaned_data

    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data.get("nombre_usuario")
        if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
            raise ValidationError("Este nombre de usuario ya está en uso")
        return nombre_usuario

    def clean_correo(self):
        correo = self.cleaned_data.get("correo")
        if Usuario.objects.filter(correo=correo).exists():
            raise ValidationError("Este correo electrónico ya está registrado")
        return correo


class LoginForm(forms.Form):
    correo = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "tu@correo.com"}
        ),
        label="Correo Electrónico",
    )
    contrasenia = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Tu contraseña"}
        ),
        label="Contraseña",
    )


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = [
            "nombre_tarea",
            "descripcion_tarea",
            "asignatura",
            "fecha_entrega",
            "prioridad",
            "modalidad",
        ]
        widgets = {
            "nombre_tarea": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre de la tarea"}
            ),
            "descripcion_tarea": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descripción detallada de la tarea",
                    "rows": 3,
                }
            ),
            "asignatura": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de la asignatura",
                }
            ),
            "fecha_entrega": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "prioridad": forms.Select(attrs={"class": "form-control"}),
            "modalidad": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "nombre_tarea": "Nombre de la Tarea",
            "descripcion_tarea": "Descripción",
            "asignatura": "Asignatura",
            "fecha_entrega": "Fecha de Entrega",
            "prioridad": "Prioridad",
            "modalidad": "Modalidad",
        }

    def clean_fecha_entrega(self):
        fecha_entrega = self.cleaned_data.get("fecha_entrega")
        if fecha_entrega and fecha_entrega < timezone.now().date():
            raise ValidationError("La fecha de entrega no puede ser en el pasado")
        return fecha_entrega
