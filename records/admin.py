from django.contrib import admin
from .models import ClinicalHistory, Consultation

@admin.register(ClinicalHistory)
class ClinicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'ultima_actualizacion')
    search_fields = ('paciente__nombre', 'paciente__cedula')

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'cita', 'diagnostico', 'estado', 'fecha_realizada')
    list_filter = ('estado',)
