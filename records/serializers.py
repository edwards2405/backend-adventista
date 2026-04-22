from rest_framework import serializers
from .models import Consultation
from appointments.models import Appointment
from datetime import date

class SOAPSerializer(serializers.Serializer):
    subjetivo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    objetivo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    analisis = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    plan = serializers.CharField(required=False, allow_blank=True, allow_null=True)

class ConsultationSerializer(serializers.ModelSerializer):
    patientId = serializers.IntegerField(write_only=True, required=True)
    soap = SOAPSerializer(write_only=True, required=True)
    diagnosis = serializers.CharField(source='diagnostico', required=False, allow_blank=True)
    
    # Read-only fields
    date = serializers.SerializerMethodField(read_only=True)
    doctor = serializers.SerializerMethodField(read_only=True)
    soap_read = serializers.SerializerMethodField(source='get_soap_read', read_only=True)
    status = serializers.CharField(source='estado', read_only=True)
    
    class Meta:
        model = Consultation
        fields = ['id', 'patientId', 'date', 'doctor', 'diagnosis', 'soap', 'soap_read', 'status']

    def to_representation(self, instance):
        # Movemos soap_read a soap para cumplir con el JSON del frontend
        ret = super().to_representation(instance)
        if 'soap_read' in ret:
            ret['soap'] = ret.pop('soap_read')
        # Añadimos el patientId real desde la cita para el GET
        ret['patientId'] = instance.cita.paciente.id
        return ret

    def get_date(self, obj):
        if obj.fecha_realizada:
            return obj.fecha_realizada.strftime('%Y-%m-%d')
        return None

    def get_doctor(self, obj):
        if obj.cita and obj.cita.especialista:
            return obj.cita.especialista.nombre_completo
        return "N/A"

    def get_soap_read(self, obj):
        return {
            "subjetivo": obj.subjetivo or "",
            "objetivo": obj.objetivo or "",
            "analisis": obj.analisis or "",
            "plan": obj.plan or ""
        }

    def create(self, validated_data):
        patient_id = validated_data.pop('patientId')
        soap_data = validated_data.pop('soap')
        diagnostico = validated_data.get('diagnostico', '')

        # Buscar la cita más reciente del paciente (idealmente de hoy)
        today = date.today()
        # Primero intentamos buscar una cita programada para hoy o antes que esté pendiente/confirmada/en_espera
        last_appt = Appointment.objects.filter(
            paciente_id=patient_id
        ).order_by('-fecha_pautada').first()

        if not last_appt:
            raise serializers.ValidationError({
                "patientId": "El paciente no tiene citas asociadas en el sistema para realizar una consulta."
            })

        # Si la cita ya tiene una consulta asociada, y no estamos actualizando, podríamos fallar.
        # Pero el requerimiento es crear. DRF OneToOneField: si creas otra que apunta a la misma cita, lanza error de integridad.
        # En caso de que la última cita ya tenga consulta, buscaremos la primera sin consulta.
        if hasattr(last_appt, 'consultation') and last_appt.consultation:
            appt_sin_consulta = Appointment.objects.filter(
                paciente_id=patient_id, 
                consultation__isnull=True
            ).order_by('fecha_pautada').last()
            
            if appt_sin_consulta:
                last_appt = appt_sin_consulta
            else:
                # Si todas sus citas tienen consulta, usaremos la última y simplemente la actualizamos 
                # (aunque para CREATE debería ser un POST nuevo, aquí manejamos el update silencioso 
                # o forzamos un error amigable). Vamos a retornar la consulta existente actualizada.
                consultation = last_appt.consultation
                consultation.diagnostico = diagnostico
                consultation.subjetivo = soap_data.get('subjetivo', consultation.subjetivo)
                consultation.objetivo = soap_data.get('objetivo', consultation.objetivo)
                consultation.analisis = soap_data.get('analisis', consultation.analisis)
                consultation.plan = soap_data.get('plan', consultation.plan)
                consultation.save()
                return consultation

        # Crear nueva consulta
        consultation = Consultation.objects.create(
            cita=last_appt,
            diagnostico=diagnostico,
            subjetivo=soap_data.get('subjetivo', ''),
            objetivo=soap_data.get('objetivo', ''),
            analisis=soap_data.get('analisis', ''),
            plan=soap_data.get('plan', ''),
            estado='abierta'
        )
        return consultation

class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['abierta', 'cerrada'])
