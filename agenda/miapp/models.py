from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
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
    
    @property
    def tareas_pendientes_count(self):
        """Cuenta las tareas pendientes del usuario"""
        hoy = timezone.now().date()
        manana = hoy + timedelta(days=1)
        
        return self.tarea_set.filter(
            Q(fecha_entrega__lte=manana) &  # Hoy o antes
            Q(estatus__nombre__in=['nue', 'pro'])  # No completadas
        ).count()
    
    @property
    def tareas_por_vencer(self):
        """Detalle de tareas por vencer"""
        hoy = timezone.now().date()
        manana = hoy + timedelta(days=1)
        
        return {
            'hoy': self.tarea_set.filter(
                fecha_entrega=hoy,
                estatus__nombre__in=['nue', 'pro']
            ).count(),
            'manana': self.tarea_set.filter(
                fecha_entrega=manana,
                estatus__nombre__in=['nue', 'pro']
            ).count(),
            'vencidas': self.tarea_set.filter(
                fecha_entrega__lt=hoy,
                estatus__nombre__in=['nue', 'pro']
            ).count(),
            'total': self.tareas_pendientes_count
        }


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
    
    modalidad = models.CharField(max_length=3, choices=MODALIDADES)
    prioridad = models.CharField(max_length=3, choices=PRIORIDADES)

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
    def dias_restantes_texto(self):
        if not self.fecha_entrega:
            return "Sin fecha límite"
        
        hoy = timezone.now().date()
        dias = (self.fecha_entrega - hoy).days
        
        if dias < 0:
            return f"Vencida hace {-dias} días"
        elif dias == 0:
            return "Vence hoy"
        elif dias == 1:
            return "Vence mañana"
        else:
            return f"{dias} días restantes"
        
    def get_modalidad_display(self):
        return dict(self.MODALIDADES).get(self.modalidad, self.modalidad)
    
    def get_prioridad_display(self):
        return dict(self.PRIORIDADES).get(self.prioridad, self.prioridad)
    
    @property
    def estado_display(self):
        """Obtener el nombre del estado para mostrar"""
        if self.estatus:
            # Si el estatus tiene get_nombre_display, usarlo
            if hasattr(self.estatus, 'get_nombre_display'):
                return self.estatus.get_nombre_display()
            # Si tiene nombre, convertirlo a display
            elif hasattr(self.estatus, 'nombre'):
                nombre = self.estatus.nombre
                if nombre == 'nue':
                    return "NUEVO"
                elif nombre == 'pro':
                    return "EN PROGRESO"
                elif nombre == 'fin':
                    return "COMPLETADO"
                else:
                    return nombre.upper()
        return "SIN ESTADO"
    
    @property
    def color_estado(self):
        """Obtener color según estado y fecha"""
        if not self.estatus:
            return '#895159'
        
        estado = self.estatus.nombre if hasattr(self.estatus, 'nombre') else ''
        hoy = datetime.now().date()
        
        # Si está vencida y no completada
        if self.fecha_entrega and self.fecha_entrega < hoy and estado != 'fin':
            return '#C44545'
        
        # Por estado
        if estado == 'fin':
            return '#6A3F46'
        elif estado == 'pro':
            return '#E6B8A8'
        elif estado == 'nue':
            return '#D5D8F0'
        
        return '#895159'


class ComentarioTarea(models.Model):
    tarea = models.ForeignKey(
        'Tarea', 
        on_delete=models.CASCADE, 
        related_name='comentarios'
    )
    usuario = models.ForeignKey(
        'Usuario', 
        on_delete=models.CASCADE, 
        related_name='comentarios_tareas'
    )
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    TIPO_CHOICES = [
        ('gen', 'General'),
        ('seg', 'Seguimiento'),
        ('obs', 'Observación'),
        ('rec', 'Recordatorio'),
    ]
    tipo = models.CharField(
        max_length=3, 
        choices=TIPO_CHOICES, 
        default='gen'
    )
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Comentario de Tarea'
        verbose_name_plural = 'Comentarios de Tareas'
    
    def __str__(self):
        return f"Comentario en {self.tarea.nombre_tarea} - {self.usuario.nombre_usuario}"
    
    @property
    def tiempo_transcurrido(self):
        ahora = timezone.now()
        diferencia = ahora - self.fecha_creacion
        
        if diferencia.days > 30:
            return f"Hace {diferencia.days // 30} mes(es)"
        elif diferencia.days > 0:
            return f"Hace {diferencia.days} día(s)"
        elif diferencia.seconds > 3600:
            return f"Hace {diferencia.seconds // 3600} hora(s)"
        elif diferencia.seconds > 60:
            return f"Hace {diferencia.seconds // 60} minuto(s)"
        else:
            return "Ahora mismo"
    
