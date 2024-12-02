# Create your models here.
from django.db import models
from datetime import date
from django.core.mail import send_mail
from django.conf import settings


from django.core.mail import EmailMessage
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

# Create your models here.
class EstadReserva(models.Model):

    estadoReservaId = models.CharField(primary_key = True,max_length = 3)
    estadoReservaNombre = models.CharField(max_length = 20)

    def __str__(self):
        return "{}".format(self.estadoReservaNombre)

class TipoReserva(models.Model):

    tipoSolicitudId = models.CharField(primary_key = True,max_length = 3)
    tipoSolicitud = models.CharField(max_length = 20)

    def __str__(self):
        return "{}".format(self.tipoSolicitud)

   
class Reserva(models.Model):

    idSolicitud = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    telefono = models.CharField(max_length=12)
    fechareserva = models.DateField()
    horareserva = models.TimeField()
    cantidadhermanos = models.IntegerField()
 
    observaciones = models.CharField(max_length=5000)
    
    website = models.URLField()
    email = models.EmailField()
    donante = models.BooleanField()
    fechanacimiento = models.DateTimeField(null=True, blank=True)
    
    estadoReservaId = models.ForeignKey(EstadReserva, null = True, blank = False, on_delete = models.RESTRICT)
    tipoSolicitudId = models.ForeignKey(TipoReserva, null = True, blank = False,  on_delete = models.RESTRICT)

    ImagenCarnet = models.ImageField(upload_to='carnets/', null=True, blank=True)
    F_Creacion = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    F_Modificacion = models.DateTimeField(auto_now_add=True, null = True, blank = True)

    def calcularEdad(self):
        hoy = date.today()
        return hoy.year - self.fechanacimiento.year - ((hoy.month, hoy.day) < (self.fechanacimiento.month, self.fechanacimiento.day))
    
    def save(self, *args, **kwargs):
        # Envía el correo solo si es una nueva reserva
        if not self.pk:  # Verifica si es un nuevo registro
            self.enviar_correo_reserva()
        super().save(*args, **kwargs)

    def enviar_correo_reserva(self):
        # Generar el PDF en memoria
        template_path = 'reserva_pdf.html'  # Asegúrate de que esta plantilla exista
        context = {'reserva': self}  # Datos para la plantilla
        template = get_template(template_path)
        html = template.render(context)

        # Crear el PDF en un buffer de memoria
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=pdf_buffer)
        pdf_buffer.seek(0)  # Volver al inicio del archivo en memoria

        if pisa_status.err:
            return  # Salir si hay un error al generar el PDF

        # Configurar el correo
        subject = f"Confirmación de tu reserva #{self.idSolicitud}"
        message = (
            f"Hola {self.nombre},\n\n"
            f"Gracias por realizar tu reserva con nosotros. En el adjunto encontrarás "
            f"los detalles de tu reserva.\n\nSaludos cordiales,\nEl equipo de Reservas"
            f"Funcionó Juli?!"
        )
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [self.email],  # Destinatario
        )

        # Adjuntar el PDF
        email.attach(f"reserva_{self.idSolicitud}.pdf", pdf_buffer.getvalue(), 'application/pdf')

        # Enviar el correo
        email.send()
    
    