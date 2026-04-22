from rest_framework import serializers
from .models import Appointment
from patients.models import Patient
from users.models import Specialist
from datetime import datetime

class AppointmentSerializer(serializers.ModelSerializer):
    patientId = serializers.CharField(source='paciente.id', read_only=True)
    patientName = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    specialty = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    type = serializers.CharField(source='motivo_consulta')
    status = serializers.CharField(source='estado', required=False)

    class Meta:
        model = Appointment
        fields = ['id', 'patientId', 'patientName', 'doctor', 'specialty', 'date', 'time', 'status', 'type']

    def get_patientName(self, obj):
        return f"{obj.paciente.nombre} {obj.paciente.apellidos}".strip()

    def get_doctor(self, obj):
        return obj.especialista.nombre_completo if obj.especialista else None

    def get_specialty(self, obj):
        return obj.especialista.especialidad if obj.especialista else None

    def get_date(self, obj):
        return obj.fecha_pautada.strftime('%Y-%m-%d') if obj.fecha_pautada else None

    def get_time(self, obj):
        return obj.fecha_pautada.strftime('%H:%M') if obj.fecha_pautada else None

    def create(self, validated_data):
        request = self.context.get('request')
        data = request.data if request else {}
        
        # Resolución de IDs y FKs basados en los strings del frontend
        patient_id = data.get('patientId')
        doctor_name = data.get('doctor')
        
        if patient_id:
            try:
                validated_data['paciente'] = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                raise serializers.ValidationError({"patientId": "Paciente no encontrado"})
                
        if doctor_name:
            # Buscar especialista por nombre exacto o aproximado
            try:
                especialista = Specialist.objects.filter(nombre_completo__icontains=doctor_name).first()
                if especialista:
                    validated_data['especialista'] = especialista
                else:
                    raise serializers.ValidationError({"doctor": "Especialista no encontrado"})
            except Exception:
                raise serializers.ValidationError({"doctor": "Error buscando especialista"})

        # Combinar date y time en fecha_pautada
        date_str = data.get('date')
        time_str = data.get('time')
        if date_str and time_str:
            try:
                dt_str = f"{date_str} {time_str}"
                validated_data['fecha_pautada'] = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            except ValueError:
                raise serializers.ValidationError({"date": "Formato de fecha u hora inválido"})
        else:
            raise serializers.ValidationError({"date": "Se requieren date y time"})

        # El status inicial siempre es 'pendiente' según los requerimientos
        validated_data['estado'] = 'pendiente'
        
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        # Este endpoint principalmente actualizará el status.
        # Si se envían otros campos, se ignorarán para mantener consistencia.
        if 'estado' in validated_data:
            instance.estado = validated_data['estado']
        instance.save()
        return instance

class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES)
