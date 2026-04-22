from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    ROLES_CHOICES = (
        ('superadmin', 'Superadmin'),
        ('recepcion', 'Recepción'),
        ('medico', 'Médico'),
    )
    nombre_rol = models.CharField(max_length=50, choices=ROLES_CHOICES, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre_rol

class User(AbstractUser):
    # AbstractUser ya incluye username, password, email, is_active (estado_activo), etc.
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    
    def __str__(self):
        return f"{self.username} ({self.role.nombre_rol if self.role else 'Sin rol'})"

class Specialist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='specialist_profile')
    cedula = models.CharField(max_length=20, unique=True)
    nombre_completo = models.CharField(max_length=150)
    especialidad = models.CharField(max_length=100)
    tlf = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_completo} - {self.especialidad}"

class Cashier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='cashier_profile')
    nombre_empleado = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre_empleado
