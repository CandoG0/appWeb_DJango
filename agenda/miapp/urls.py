from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'miapp'

urlpatterns = [
    
    # views.crear_tarea viene de la carpeta miapp views.py despues del def
    path("tareas/", views.listar_tareas, name="listar_tareas"),
    path("tareas/crear/", views.crear_tarea, name="crear_tarea"),

    path("tareas/vencer/", views.tareas_vencer, name="tareas_vencer"),
    path("tareas/pendientes/", views.tareas_pendientes, name="tareas_pendientes"),
    path("tareas/completadas/", views.tareas_completadas, name="tareas_completadas"),
    
    path("tareas/detalle/<int:tarea_id>/", views.detalle_tarea, name="detalle_tarea"),
    path("tareas/editar/<int:tarea_id>/", views.editar_tarea, name="editar_tarea"),
    path("tareas/eliminar/<int:tarea_id>/", views.eliminar_tarea, name="eliminar_tarea"),

    path("tareas/completar/<int:tarea_id>/", views.marcar_completada, name="marcar_completada"),
    path("tareas/actualizar/<int:tarea_id>/", views.actualizar_estado, name="actualizar_estado"),
    
    path('calendario/', views.calendario_view, name='calendario'),
    path('api/tareas-calendario/', views.tareas_calendario_api, name='tareas_calendario_api'),
    path('editar-perfil/', views.perfil_usuario, name='perfil_usuario'),
]
