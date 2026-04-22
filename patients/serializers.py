from rest_framework import serializers
from .models import Patient, Allergy, Pathology
from datetime import date
from appointments.models import Appointment

class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ['id', 'nombre']

class PathologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pathology
        fields = ['id', 'nombre']

class PatientSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    dob = serializers.DateField(source='fecha_nacimiento', required=False, allow_null=True)
    gender = serializers.CharField(source='genero', required=False)
    phone = serializers.CharField(source='telefono', required=False, allow_blank=True)
    email = serializers.EmailField(source='correo', required=False, allow_blank=True)
    status = serializers.CharField(source='estado_paciente', required=False)
    bloodType = serializers.CharField(source='tipo_sangre', required=False)
    insurance = serializers.CharField(source='seguro_medico', required=False, allow_blank=True, allow_null=True)
    
    alergias = serializers.SerializerMethodField()
    lastVisit = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    specialty = serializers.SerializerMethodField()
    vitalSigns = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'cedula', 'name', 'age', 'gender', 'phone', 'email', 'dob',
            'alergias', 'status', 'bloodType', 'insurance', 'lastVisit',
            'doctor', 'specialty', 'vitalSigns',
            # Campos extra de escritura que no mapean 1:1 al frontend GET:
            'nombre', 'apellidos', 'genero'
        ]
        extra_kwargs = {
            'nombre': {'write_only': True, 'required': False},
            'apellidos': {'write_only': True, 'required': False},
            'genero': {'write_only': True, 'required': False},
            'cedula': {'required': False}
        }

    def get_name(self, obj):
        return f"{obj.nombre} {obj.apellidos}".strip()

    def get_age(self, obj):
        if not obj.fecha_nacimiento:
            return None
        today = date.today()
        return today.year - obj.fecha_nacimiento.year - ((today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day))

    def get_alergias(self, obj):
        if hasattr(obj, 'clinical_history') and obj.clinical_history:
            return [alergia.nombre for alergia in obj.clinical_history.alergias.all()]
        return []

    def _get_last_appointment(self, obj):
        # Cacheamos la última cita para no hacer múltiples queries
        if not hasattr(self, '_last_appointment'):
            self._last_appointment = obj.appointments.filter(estado='completada').order_by('-fecha_pautada').first()
        return self._last_appointment

    def get_lastVisit(self, obj):
        appt = self._get_last_appointment(obj)
        if appt:
            return appt.fecha_pautada.strftime('%Y-%m-%d')
        return None

    def get_doctor(self, obj):
        appt = self._get_last_appointment(obj)
        if appt and appt.especialista:
            return appt.especialista.nombre_completo
        return None

    def get_specialty(self, obj):
        appt = self._get_last_appointment(obj)
        if appt and appt.especialista:
            return appt.especialista.especialidad
        return None

    def get_vitalSigns(self, obj):
        appt = self._get_last_appointment(obj)
        if appt and hasattr(appt, 'consultation') and appt.consultation:
            c = appt.consultation
            return {
                "bp": c.tension_arterial,
                "hr": c.frecuencia_cardiaca,
                "temp": float(c.temperatura) if c.temperatura else None,
                "spo2": c.saturacion_oxigeno,
                "weight": float(c.peso) if c.peso else None,
                "bmi": float(c.imc) if c.imc else None
            }
        # Si no hay signos vitales
        return {
            "bp": "-",
            "hr": 0,
            "temp": 0,
            "spo2": 0,
            "weight": 0,
            "bmi": 0
        }

    def create(self, validated_data):
        # Frontend manda `name` (a veces "Nombre Apellidos")
        request = self.context.get('request')
        if request and 'name' in request.data:
            parts = request.data['name'].split(' ', 1)
            validated_data['nombre'] = parts[0]
            validated_data['apellidos'] = parts[1] if len(parts) > 1 else ''
            
        if request and 'gender' in request.data:
            validated_data['genero'] = request.data['gender']
            
        # Si no mandan dob explícito en POST pero es requerido por el modelo
        if 'fecha_nacimiento' not in validated_data:
            validated_data['fecha_nacimiento'] = date.today()
            
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and 'name' in request.data:
            parts = request.data['name'].split(' ', 1)
            validated_data['nombre'] = parts[0]
            validated_data['apellidos'] = parts[1] if len(parts) > 1 else ''
            
        if request and 'gender' in request.data:
            validated_data['genero'] = request.data['gender']
            
        return super().update(instance, validated_data)

class VitalSignsUpdateSerializer(serializers.Serializer):
    bp = serializers.CharField(required=False, allow_blank=True)
    hr = serializers.IntegerField(required=False)
    temp = serializers.FloatField(required=False)
    spo2 = serializers.IntegerField(required=False)
    weight = serializers.FloatField(required=False)
    bmi = serializers.FloatField(required=False)
