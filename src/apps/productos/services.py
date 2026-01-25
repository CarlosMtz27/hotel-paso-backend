# La lógica de negocio que estaba en esta capa de servicios ha sido
# movida a los serializadores de DRF (`serializers.py`) para centralizar
# la validación y aprovechar las características de Django REST Framework.
#
# Las vistas (`views.py`) ahora utilizan vistas genéricas que se integran
# directamente con los serializadores, simplificando el código.