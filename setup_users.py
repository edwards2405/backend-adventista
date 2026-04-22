import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import User, Role

def setup():
    # Roles
    r_super, _ = Role.objects.get_or_create(nombre_rol='superadmin', descripcion='Super Administrador')
    r_med, _ = Role.objects.get_or_create(nombre_rol='medico', descripcion='Médico Especialista')
    r_rec, _ = Role.objects.get_or_create(nombre_rol='recepcion', descripcion='Personal de Recepción')
    
    # Admin
    if not User.objects.filter(email='admin@hav.edu.ve').exists():
        admin = User.objects.create_superuser(username='admin', email='admin@hav.edu.ve', password='admin123', role=r_super)
        print("Creado admin@hav.edu.ve")
    
    # Médico
    if not User.objects.filter(email='medico@hav.edu.ve').exists():
        medico = User.objects.create_user(username='medico', email='medico@hav.edu.ve', password='admin123', role=r_med)
        from users.models import Specialist
        Specialist.objects.create(user=medico, cedula='V-11111111', nombre_completo='Dr. Ricardo Pérez', especialidad='Cardiología')
        print("Creado medico@hav.edu.ve")
        
    # Recepción
    if not User.objects.filter(email='recepcion@hav.edu.ve').exists():
        recepcion = User.objects.create_user(username='recepcion', email='recepcion@hav.edu.ve', password='admin123', role=r_rec)
        print("Creado recepcion@hav.edu.ve")

setup()
