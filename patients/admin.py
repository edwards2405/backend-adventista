from django.contrib import admin
from .models import Patient, Allergy, Pathology

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'cedula', 'estado_paciente', 'fecha_registro')
    search_fields = ('nombre', 'apellidos', 'cedula')
    list_filter = ('estado_paciente', 'genero')

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Pathology)
class PathologyAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
