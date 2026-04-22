from django.db import models

class Patient(models.Model):
    GENDER_CHOICES = (
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
    )
    BLOOD_TYPE_CHOICES = (
        ('O+', 'O+'), ('O-', 'O-'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    )
    STATUS_CHOICES = (
        ('activo', 'Activo'),
        ('pendiente', 'Pendiente'),
        ('dado_de_alta', 'Dado de alta'),
    )

    cedula = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=20, choices=GENDER_CHOICES)
    seguro_medico = models.CharField(max_length=150, blank=True, null=True)
    estado_paciente = models.CharField(max_length=50, choices=STATUS_CHOICES, default='activo')
    tipo_sangre = models.CharField(max_length=5, choices=BLOOD_TYPE_CHOICES)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField(blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    nombre_contacto_emergencia = models.CharField(max_length=150, blank=True, null=True)
    tlf_contacto_emergencia = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.cedula}"

class Allergy(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Pathology(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
