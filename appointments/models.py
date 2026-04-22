from django.db import models
from patients.models import Patient
from users.models import Specialist, Cashier

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('confirmada', 'Confirmada'),
        ('en_espera', 'En espera'),
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
    )
    TYPE_CHOICES = (
        ('Control', 'Control'),
        ('Consulta Nueva', 'Consulta Nueva'),
        ('Primera Vez', 'Primera Vez'),
        ('Urgencia', 'Urgencia'),
    )

    paciente = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    especialista = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='appointments')
    motivo_consulta = models.CharField(max_length=255, choices=TYPE_CHOICES)
    estado = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pendiente')
    fecha_pautada = models.DateTimeField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cita {self.id} - {self.paciente.nombre} con {self.especialista.nombre_completo}"

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pagado', 'Pagado'),
        ('pendiente', 'Pendiente'),
        ('anulado', 'Anulado'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('seguro', 'Seguro'),
    )

    cita = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    paciente = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    caja = models.ForeignKey(Cashier, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payments')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    estado_pago = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pendiente')
    fecha_pago = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago {self.id} - Cita {self.cita.id}"
