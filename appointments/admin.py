from django.contrib import admin
from .models import Appointment, Payment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'especialista', 'estado', 'fecha_pautada')
    list_filter = ('estado', 'motivo_consulta')
    search_fields = ('paciente__nombre', 'especialista__nombre_completo')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'cita', 'monto', 'estado_pago', 'metodo_pago')
    list_filter = ('estado_pago', 'metodo_pago')
