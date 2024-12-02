from django.contrib import admin

# Register your models here.
from .models import Reserva, EstadReserva, TipoReserva

# Registro básico
admin.site.register(Reserva)
admin.site.register(EstadReserva)
admin.site.register(TipoReserva)