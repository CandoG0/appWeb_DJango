from .models import Usuario

def usuario_actual(request):
    """Agrega el objeto Usuario al contexto de todas las plantillas"""
    usuario = None
    usuario_id = request.session.get('usuario_id')
    
    if usuario_id:
        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            pass
    
    return {
        'usuario_actual': usuario
    }