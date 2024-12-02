from django.shortcuts import render, redirect

# Create your views here.
from .models import Reserva
from .forms import ReservaForm
from django.core.mail import send_mail
from django.conf import settings

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import base64

from django.shortcuts import get_object_or_404
from django.urls import reverse

# Create your views here.
def agregarReserva(request):
    form = ReservaForm()
    if request.method == 'POST':
        # Incluye request.FILES para manejar archivos subidos
        form = ReservaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = ReservaForm()  # Reinicia el formulario después de guardar
        
    reservas = Reserva.objects.all()
    data = {'form': form, 'reservas': reservas}
    return render(request, 'templatesApp/agregar.html', data)


def eliminarReserva(request, id):
    reserva =Reserva.objects.get(idSolicitud=id)
    reserva.delete()
    return redirect('/')

def actualizarReserva(request, id):
    reserva = Reserva.objects.get(idSolicitud=id)
    form = ReservaForm(instance=reserva)
    if (request.method == 'POST'):
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            form = ReservaForm()
                    
    reservas = Reserva.objects.all()
    data = {'form': form, 'reservas': reservas}
    return render(request, 'templatesApp/agregar.html',data)

def generar_pdf(request, reserva_id):
    reserva = get_object_or_404(Reserva, idSolicitud=reserva_id)

    # Generar la URL absoluta para la imagen
    imagen_url = None
    if reserva.ImagenCarnet:
        imagen_url = request.build_absolute_uri(reserva.ImagenCarnet.url)

    # Contexto para la plantilla
    context = {
        'reserva': reserva,
        'imagen_url': imagen_url  # Pasar la URL absoluta al contexto
    }

    # Crear el PDF
    template_path = 'reserva_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reserva_{reserva.idSolicitud}.pdf"'

    # Renderizar contenido HTML
    template = get_template(template_path)
    html = template.render(context)

    # Generar el PDF con soporte para imágenes
    pisa_status = pisa.CreatePDF(
        html, dest=response
    )

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)
    return response

def generar_solo_qr_pdf(request, reserva_id):
    try:
        reserva = Reserva.objects.get(idSolicitud=reserva_id)
    except Reserva.DoesNotExist:
        return HttpResponse("Reserva no encontrada.", status=404)

    # Genera la URL dinámica para el PDF
    pdf_url = request.build_absolute_uri(reverse('generar_pdf', args=[reserva_id]))

    # Generar el QR con el enlace al PDF
    qr_code = qrcode.make(pdf_url)
    qr_buffer = BytesIO()
    qr_code.save(qr_buffer, format="PNG")
    qr_image_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')

    # Contexto para la plantilla
    context = {
        'reserva': reserva,
        'qr_code': qr_image_base64,
        'pdf_url': pdf_url
    }

    # Crear el PDF con el QR
    template_path = 'qr_pdf.html'  # Plantilla específica para el QR
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="qr_reserva_{reserva.idSolicitud}.pdf"'

    # Renderizar HTML
    template = get_template(template_path)
    html = template.render(context)

    # Generar el PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF del QR', status=400)
    return response