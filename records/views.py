from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.db.models import Count
from django.utils.timezone import now

from .models import Consultation
from .serializers import ConsultationSerializer, StatusUpdateSerializer
from appointments.models import Appointment
from patients.models import Patient
from users.models import User
from users.permissions import IsAdmin, IsReceptionist

class ClinicalHistoryViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all().order_by('-fecha_realizada')
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Historia Clínica'],
        summary="Listar Historias Clínicas",
        description="Obtiene el historial clínico de un paciente específico.",
        parameters=[
            OpenApiParameter("patientId", OpenApiTypes.INT, description="ID del paciente", required=True),
            OpenApiParameter("status", OpenApiTypes.STR, description="Filtrar por estado (abierta, cerrada)", required=False),
        ]
    )
    def list(self, request, *args, **kwargs):
        patient_id = request.query_params.get('patientId')
        status_param = request.query_params.get('status')

        if not patient_id:
            return Response({"success": False, "message": "patientId es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(cita__paciente_id=patient_id)
        
        if status_param:
            queryset = queryset.filter(estado=status_param)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

    @extend_schema(
        tags=['Historia Clínica'],
        summary="Crear Historia Clínica (SOAP)",
        description="Guarda una nueva entrada de historia clínica (nota SOAP). Solo médico o admin."
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # El create del serializer maneja la lógica de buscar la cita y vincularla
        consultation = serializer.save()
        
        # Volver a serializar para responder con el formato GET (incluyendo doctor, date, etc)
        response_serializer = self.get_serializer(consultation)
        
        return Response({
            "success": True,
            "data": response_serializer.data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Historia Clínica'],
        summary="Cerrar/Abrir Historia",
        request=StatusUpdateSerializer,
        methods=["PATCH"]
    )
    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        consultation = self.get_object()
        serializer = StatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            consultation.estado = serializer.validated_data['status']
            consultation.save()
            
            # Si cerramos la consulta, podríamos querer marcar la cita como completada
            if consultation.estado == 'cerrada':
                cita = consultation.cita
                cita.estado = 'completada'
                cita.save()
                
            response_serializer = self.get_serializer(consultation)
            return Response({
                "success": True,
                "data": response_serializer.data
            })
            
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DashboardSuperAdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=['Dashboard'],
        summary="Dashboard SuperAdmin",
        description="Estadísticas generales del sistema para el panel principal."
    )
    def get(self, request):
        today = now().date()
        
        # Pacientes atendidos hoy (Consultas creadas hoy)
        patients_attended_today = Consultation.objects.filter(fecha_realizada__date=today).count()
        
        # Personal
        active_staff = User.objects.filter(is_active=True).count()
        total_staff = User.objects.count()
        
        # Citas programadas hoy
        scheduled_appointments = Appointment.objects.filter(fecha_pautada__date=today).count()
        
        # Nuevos registros (Pacientes) hoy
        new_registrations = Patient.objects.filter(fecha_registro__date=today).count()
        
        # Flujo por especialidad (citas de hoy agrupadas por especialidad del doctor)
        specialties = Appointment.objects.filter(fecha_pautada__date=today).values(
            'especialista__especialidad'
        ).annotate(count=Count('id'))
        
        specialty_flow = []
        for sp in specialties:
            specialty_name = sp['especialista__especialidad'] or 'General'
            specialty_flow.append({
                "name": specialty_name,
                "count": sp['count'],
                "max": 50 # Mock max
            })
            
        # Citas mensuales
        monthly_appointments = Appointment.objects.filter(
            fecha_pautada__year=today.year, 
            fecha_pautada__month=today.month
        ).count()

        return Response({
            "success": True,
            "data": {
                "patientsAttendedToday": patients_attended_today,
                "patientsAttendedDelta": "+12%", # Mock delta
                "activeStaffCount": active_staff,
                "totalStaffCount": total_staff,
                "scheduledAppointments": scheduled_appointments,
                "newRegistrations": new_registrations,
                "specialtyFlow": specialty_flow,
                "monthlyAppointments": {
                    "current": monthly_appointments,
                    "target": 2500
                }
            }
        })

class DashboardRecepcionView(APIView):
    permission_classes = [IsAuthenticated, IsReceptionist]

    @extend_schema(
        tags=['Dashboard'],
        summary="Dashboard Recepción",
        description="Estadísticas del día para el panel de recepción."
    )
    def get(self, request):
        today = now().date()
        
        appointments_today = Appointment.objects.filter(fecha_pautada__date=today)
        
        today_total = appointments_today.count()
        confirmed_count = appointments_today.filter(estado='confirmada').count()
        waiting_count = appointments_today.filter(estado='en_espera').count()
        attended_count = appointments_today.filter(estado='completada').count()

        return Response({
            "success": True,
            "data": {
                "todayAppointments": today_total,
                "confirmedCount": confirmed_count,
                "waitingCount": waiting_count,
                "attendedCount": attended_count
            }
        })
