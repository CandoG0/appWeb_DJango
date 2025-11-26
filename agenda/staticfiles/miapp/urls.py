from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'miapp'

urlpatterns = [
    
    # views.crear_tarea viene de la carpeta miapp views.py despues del def
    path("tareas/", views.listar_tareas, name="listar_tareas"),
    path("tareas/crear/", views.crear_tarea, name="crear_tarea"),
    #aqui va para editar tarea
    #aqui va para eliminar tarea
    path("tareas/vencer/", views.tareas_vencer, name="tareas_vencer"),
    path("tareas/pendientes/", views.tareas_pendientes, name="tareas_pendientes"),
    path("tareas/completar/<int:tarea_id>/", views.marcar_completada, name="marcar_completada"),
    path("tareas/completadas/", views.tareas_completadas, name="tareas_completadas"),
    path("detalle_tarea/", views.detalle_tarea, name="detalle_tarea"),
    path("calendario/", views.calendario, name="calendario"),
]
