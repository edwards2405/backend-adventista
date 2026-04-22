from django.db import models
from patients.models import Patient, Allergy, Pathology
from appointments.models import Appointment

class ClinicalHistory(models.Model):
    paciente = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='clinical_history')
    cirugias = models.TextField(blank=True, null=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    # Relaciones ManyToMany para alergias y patologías (crea tablas puente automáticamente)
    alergias = models.ManyToManyField(Allergy, blank=True, related_name='historiales')
    patologias = models.ManyToManyField(Pathology, blank=True, related_name='historiales')

    def __str__(self):
        return f"Historial de {self.paciente.nombre} {self.paciente.apellidos}"

class Consultation(models.Model):
    STATUS_CHOICES = (
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    )

    cita = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    
    # SOAP
    subjetivo = models.TextField(blank=True, null=True)
    objetivo = models.TextField(blank=True, null=True)
    analisis = models.TextField(blank=True, null=True)
    plan = models.TextField(blank=True, null=True)
    
    diagnostico = models.CharField(max_length=255, blank=True, null=True)
    tratamiento = models.TextField(blank=True, null=True)
    
    # Signos Vitales
    tension_arterial = models.CharField(max_length=20, blank=True, null=True)
    frecuencia_cardiaca = models.IntegerField(blank=True, null=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    saturacion_oxigeno = models.IntegerField(blank=True, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    imc = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    
    estado = models.CharField(max_length=50, choices=STATUS_CHOICES, default='abierta')
    fecha_realizada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consulta {self.id} - Cita {self.cita.id}"
