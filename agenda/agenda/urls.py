from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('miapp/', include('miapp.urls')),
    
    # SOLUCIÓN: Redirigir la raíz al login
    path('', RedirectView.as_view(url='/login/'), name='home'),
    path('', include('home.urls')),  # Mantener esta línea para otras rutas de home

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)