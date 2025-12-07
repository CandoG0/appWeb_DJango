from django.contrib import admin

from miapp.models import Estatu, Tarea, Usuario, ComentarioTarea

# Register your models here.
admin.site.register(Estatu)
admin.site.register(Usuario)
admin.site.register(Tarea)
admin.site.register(ComentarioTarea)
