from django.urls import path
from . import views

urlpatterns = [
    # Las url nos sirve para establecer endpoints, agregar a la url base otro fragmento para identificar a la vista
    # Ademas de eso ayudan a traer la logica de cada vista asi como a renderizarla, también establece el nombre con el cual debera ser invocado en el html
    # views.login viene de la carpeta home views.py
    path("login/", views.login, name="login"), # vista inicial
    path("registrar/", views.registrar, name="registrar"),
    path("logout/", views.logout, name="logout"),
    
    # URL de aplicacion
    # De las vistas trae la vista index (que es la funcion de la vista)
    path("inicio/", views.index, name="index"),
]

