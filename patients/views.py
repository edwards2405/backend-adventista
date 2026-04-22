from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import Patient
from .serializers import PatientSerializer, VitalSignsUpdateSerializer
from users.permissions import IsReceptionist
from records.models import Consultation

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-fecha_registro')
    serializer_class = PatientSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsReceptionist()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=['Pacientes'],
        summary="Listar Pacientes",
        description="Lista todos los pacientes. Soporta búsqueda por nombre o cédula, y filtro por estado.",
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, description="Buscar por nombre o cédula", required=False),
            OpenApiParameter("status", OpenApiTypes.STR, description="Filtrar por estado (activo, pendiente, dado_de_alta)", required=False),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Filtros manuales simples
        search = request.query_params.get('search', None)
        status_param = request.query_params.get('status', None)
        
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(apellidos__icontains=search) | 
                Q(cedula__icontains=search)
            )
            
        if status_param:
            queryset = queryset.filter(estado_paciente=status_param)

        # Paginación default de DRF
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Adaptamos formato al frontend
            return Response({
                "success": True,
                "data": serializer.data,
                "total": self.paginator.page.paginator.count,
                "page": self.paginator.page.number,
                "totalPages": self.paginator.page.paginator.num_pages
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "total": queryset.count(),
            "page": 1,
            "totalPages": 1
        })

    @extend_schema(tags=['Pacientes'], summary="Obtener Paciente", description="Obtiene un paciente por ID")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })

    @extend_schema(tags=['Pacientes'], summary="Crear Paciente", description="Registra un nuevo paciente (Solo Recepción/Admin)")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(tags=['Pacientes'], summary="Actualizar Paciente", description="Actualiza parcialmente los datos del paciente")
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True) # Forzamos a que PUT actúe como PATCH (partial=True) para facilitar uso desde React
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "data": serializer.data
        })

    @extend_schema(
        tags=['Pacientes'],
        summary="Actualizar Signos Vitales",
        description="Actualiza los signos vitales del paciente en su consulta abierta más reciente",
        request=VitalSignsUpdateSerializer,
        methods=["PUT"]
    )
    @action(detail=True, methods=['put'], url_path='vital-signs')
    def vital_signs(self, request, pk=None):
        patient = self.get_object()
        
        # Necesitamos la consulta más reciente para guardar signos vitales
        last_appt = patient.appointments.order_by('-fecha_pautada').first()
        if not last_appt:
            return Response({"success": False, "message": "El paciente no tiene citas asociadas"}, status=400)
            
        if not hasattr(last_appt, 'consultation') or not last_appt.consultation:
            # Creamos una consulta si no existe
            c = Consultation.objects.create(cita=last_appt, estado='abierta')
        else:
            c = last_appt.consultation

        serializer = VitalSignsUpdateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if 'bp' in data: c.tension_arterial = data['bp']
            if 'hr' in data: c.frecuencia_cardiaca = data['hr']
            if 'temp' in data: c.temperatura = data['temp']
            if 'spo2' in data: c.saturacion_oxigeno = data['spo2']
            if 'weight' in data: c.peso = data['weight']
            if 'bmi' in data: c.imc = data['bmi']
            
            c.save()
            
            # Devolver los signos vitales actualizados (formato frontend)
            return Response({
                "success": True,
                "data": {
                    "bp": c.tension_arterial,
                    "hr": c.frecuencia_cardiaca,
                    "temp": float(c.temperatura) if c.temperatura else None,
                    "spo2": c.saturacion_oxigeno,
                    "weight": float(c.peso) if c.peso else None,
                    "bmi": float(c.imc) if c.imc else None
                }
            })
            
        return Response({"success": False, "errors": serializer.errors}, status=400)
