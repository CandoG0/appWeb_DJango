from django.db import models
from django.utils import timezone
# Create your models here.

class Estatu(models.Model):
    ESTATUS = [
        ('nue', 'Nuevo'),
        ('pro', 'En proceso'),
        ('fin', 'Finalizado'),
    ]

    nombre = models.CharField(max_length=20, choices=ESTATUS)

    def __str__(self):
        return self.get_nombre_display()


class Usuario(models.Model):
    nombre = models.CharField(max_length=20)
    appat = models.CharField(max_length=20, verbose_name="Apellido Paterno")
    apmat = models.CharField(max_length=20, verbose_name="Apellido Materno")
    nombre_usuario = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    correo = models.EmailField(unique=True, max_length=50)
    contrasenia = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['appat', 'apmat', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.appat} {self.apmat}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.appat} {self.apmat}"


class Tarea(models.Model):
    PRIORIDADES = [
        ('alt', 'Alta'),
        ('med', 'Media'),
        ('baj', 'Baja'),
    ]

    MODALIDADES = [
        ('ind', 'Individual'),
        ('grup', 'En Grupo'),
    ]

    nombre_tarea = models.CharField(max_length=100)
    descripcion_tarea = models.TextField(max_length=500)
    asignatura = models.CharField(max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateField()
    prioridad = models.CharField(
        max_length=10, choices=PRIORIDADES, default='med')
    modalidad = models.CharField(
        max_length=15, choices=MODALIDADES, default='ind')
    estatus = models.ForeignKey(
        Estatu, on_delete=models.RESTRICT, default=1)  # Default "Nuevo"

    # Relación con Usuario
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ['fecha_entrega', 'prioridad']

    def __str__(self):
        return f"{self.nombre_tarea} - {self.estatus.nombre}"

    @property
    def esta_vencida(self):
        return timezone.now() > self.fecha_entrega and self.estatus.nombre != 'fin'

    @property
    def dias_restantes(self):
        if self.estatus.nombre == 'fin':
            return "Completada"
        dias = (self.fecha_entrega - timezone.now()).days
        if dias < 0:
            return "Vencida"
        return f"{dias} días"
