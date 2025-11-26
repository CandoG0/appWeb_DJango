from django.urls import path
from . import views

urlpatterns = [
    # espacio para declarar enlaces, de las vistas jale la vista index (que es la funcion de la vista)
    # views.login viene de la carpeta home views.py despues del def
    # URL de autenticacion
    path("login/", views.login, name="login"), # vista inicial
    path("registrar/", views.registrar, name="registrar"),
    path("logout/", views.logout, name="logout"),
    
    # URL de aplicacion
    path("inicio/", views.index, name="index"),
]

