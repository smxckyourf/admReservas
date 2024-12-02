from django.urls import path
from . import views

app_name = 'App'  # Este nombre debe coincidir con el que usas en el template

urlpatterns = [
    path('agregar/', views.agregarReserva, name='agregarReserva'),  # Aquí registras la vista
]