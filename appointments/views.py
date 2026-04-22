from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.db.models import Q
from datetime import datetime

from .models import Appointment
from .serializers import AppointmentSerializer, StatusUpdateSerializer
from users.permissions import IsReceptionist

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by('fecha_pautada')
    serializer_class = AppointmentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsReceptionist()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=['Citas'],
        summary="Listar Citas",
        description="Lista las citas médicas con filtros por fecha, rango de fechas, mes, año, estado y doctor.",
        parameters=[
            OpenApiParameter("date", OpenApiTypes.STR, description="Fecha exacta (YYYY-MM-DD)", required=False),
            OpenApiParameter("dateFrom", OpenApiTypes.STR, description="Rango desde (YYYY-MM-DD)", required=False),
            OpenApiParameter("dateTo", OpenApiTypes.STR, description="Rango hasta (YYYY-MM-DD)", required=False),
            OpenApiParameter("status", OpenApiTypes.STR, description="Estado (confirmada, en_espera, pendiente, completada)", required=False),
            OpenApiParameter("doctor", OpenApiTypes.STR, description="Nombre del doctor", required=False),
            OpenApiParameter("month", OpenApiTypes.INT, description="Mes (1-12)", required=False),
            OpenApiParameter("year", OpenApiTypes.INT, description="Año", required=False),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filtros
        date_param = request.query_params.get('date')
        date_from = request.query_params.get('dateFrom')
        date_to = request.query_params.get('dateTo')
        status_param = request.query_params.get('status')
        doctor = request.query_params.get('doctor')
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if date_param:
            queryset = queryset.filter(fecha_pautada__date=date_param)
        
        if date_from:
            queryset = queryset.filter(fecha_pautada__date__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(fecha_pautada__date__lte=date_to)

        if month and year:
            queryset = queryset.filter(fecha_pautada__year=year, fecha_pautada__month=month)

        if status_param:
            queryset = queryset.filter(estado=status_param)

        if doctor:
            queryset = queryset.filter(especialista__nombre_completo__icontains=doctor)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "total": queryset.count()
        })

    @extend_schema(tags=['Citas'], summary="Obtener Cita")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })

    @extend_schema(tags=['Citas'], summary="Crear Cita", description="Crea una cita (Solo Recepción)")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Obtenemos la instancia recién creada para devolver el payload completo con los strings (patientName, etc)
        instance = Appointment.objects.get(id=serializer.instance.id)
        response_serializer = self.get_serializer(instance)
        
        return Response({
            "success": True,
            "data": response_serializer.data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Citas'],
        summary="Actualizar Estado de la Cita",
        request=StatusUpdateSerializer,
        methods=["PATCH"]
    )
    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        instance = self.get_object()
        serializer = StatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            # Validaciones simples de negocio (opcionales pero recomendadas según doc)
            # "pendiente → confirmada, confirmada → completada, en_espera → confirmada"
            # Asumiremos que el frontend hace la validación primaria, pero actualizamos:
            instance.estado = new_status
            instance.save()
            
            response_serializer = self.get_serializer(instance)
            return Response({
                "success": True,
                "data": response_serializer.data
            })
            
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=['Citas'], summary="Eliminar Cita")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "message": "Cita eliminada"
        })
