from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiTypes
from .models import User, Role
from .serializers import UserSerializer, LoginRequestSerializer, LoginResponseSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Autenticación y Usuarios'],
        summary="Iniciar sesión",
        description="Endpoint para que los usuarios inicien sesión usando su email y contraseña.",
        request=LoginRequestSerializer,
        responses={
            200: LoginResponseSerializer,
            401: OpenApiResponse(description="Credenciales incorrectas")
        }
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Buscamos al usuario por correo primero
        try:
            user_obj = User.objects.get(email=email)
            # Authenticate valida la contraseña con el sistema de hashing de Django
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            # Bug 3 fix: Verificar si el usuario está activo antes de emitir token
            if not user.is_active:
                return Response({
                    "success": False,
                    "message": "Su cuenta está desactivada. Contacte al administrador."
                }, status=status.HTTP_403_FORBIDDEN)

            # Generamos el token JWT manualmente para controlar exactamente el formato de respuesta
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            
            return Response({
                "success": True,
                "token": str(refresh.access_token),
                "user": user_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": "Credenciales incorrectas"
            }, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        tags=['Autenticación y Usuarios'],
        summary="Cerrar sesión",
        description="Endpoint para que los usuarios cierren sesión.",
        responses={
            200: {"type": "object", "properties": {"success": {"type": "boolean"}, "message": {"type": "string"}}}
        }
    )
    def post(self, request):
        # Para JWT, normalmente el logout se maneja del lado del cliente borrando el token.
        # Podríamos hacer blacklist del token aquí si fuera necesario.
        return Response({
            "success": True,
            "message": "Sesión cerrada"
        }, status=status.HTTP_200_OK)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Autenticación y Usuarios'],
        summary="Obtener usuario actual",
        description="Retorna la información del usuario autenticado basado en el token JWT.",
        responses={200: UserSerializer}
    )
    def get(self, request):
        # Ya que IsAuthenticated verificó el token, request.user tiene el objeto del usuario.
        user_data = UserSerializer(request.user).data
        return Response({
            "success": True,
            "user": user_data
        }, status=status.HTTP_200_OK)

from rest_framework import viewsets
from rest_framework.decorators import action
from django.db.models import Q
from .permissions import IsAdmin
from .serializers import StaffSerializer, StaffStatusUpdateSerializer, StaffCreateSerializer

class StaffViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False).order_by('-date_joined')
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        tags=['Personal'],
        summary="Listar Personal",
        description="Lista todo el personal del hospital. Soporta búsqueda. Solo Superadmin.",
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, description="Buscar por nombre o correo", required=False),
            OpenApiParameter("role", OpenApiTypes.STR, description="Filtrar por rol", required=False),
            OpenApiParameter("status", OpenApiTypes.STR, description="activo, inactivo", required=False),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        search = request.query_params.get('search')
        role_param = request.query_params.get('role')
        status_param = request.query_params.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) | 
                Q(email__icontains=search) |
                Q(username__icontains=search)
            )
            
        if role_param:
            queryset = queryset.filter(role__nombre_rol=role_param)
            
        if status_param == 'activo':
            queryset = queryset.filter(is_active=True)
        elif status_param == 'inactivo':
            queryset = queryset.filter(is_active=False)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "total": queryset.count()
        })

    @extend_schema(tags=['Personal'], summary="Obtener Personal")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })

    @extend_schema(tags=['Personal'], summary="Crear Personal", description="Registra un nuevo miembro del personal (Solo Superadmin)", request=StaffCreateSerializer)
    def create(self, request, *args, **kwargs):
        serializer = StaffCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        name_parts = data['name'].split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Verificar que el email no esté en uso
        if User.objects.filter(email=data['email']).exists():
            return Response({"success": False, "message": "Ya existe un usuario con ese correo electrónico"}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener o crear el rol
        role_obj, _ = Role.objects.get_or_create(nombre_rol=data['role'])

        # Crear el usuario
        user = User.objects.create_user(
            username=data['email'].split('@')[0],  # username basado en email
            email=data['email'],
            password=data.get('password', 'admin123'),
            first_name=first_name,
            last_name=last_name,
            role=role_obj,
            is_active=True,
        )

        response_serializer = StaffSerializer(user)
        return Response({"success": True, "data": response_serializer.data}, status=status.HTTP_201_CREATED)

    @extend_schema(tags=['Personal'], summary="Actualizar Personal")
    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(tags=['Personal'], summary="Actualizar Personal (parcial)")
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Actualizar rol si viene en el request
        new_role = request.data.get('role')
        if new_role:
            role_obj, _ = Role.objects.get_or_create(nombre_rol=new_role)
            instance.role = role_obj

        # Actualizar nombre si viene
        new_name = request.data.get('name')
        if new_name:
            name_parts = new_name.split(' ', 1)
            instance.first_name = name_parts[0]
            instance.last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Actualizar email si viene
        new_email = request.data.get('email')
        if new_email:
            instance.email = new_email

        instance.save()
        response_serializer = StaffSerializer(instance)
        return Response({"success": True, "data": response_serializer.data})

    @extend_schema(
        tags=['Personal'],
        summary="Activar/Desactivar Personal",
        request=StaffStatusUpdateSerializer,
        methods=["PATCH"]
    )
    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        instance = self.get_object()
        serializer = StaffStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            instance.is_active = (new_status == 'activo')
            instance.save()
            
            response_serializer = self.get_serializer(instance)
            return Response({
                "success": True,
                "data": response_serializer.data
            })
            
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=['Personal'], summary="Eliminar Personal (soft delete)")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Soft delete: marcamos como eliminado pero no borramos de la BD
        instance.is_deleted = True
        instance.is_active = False
        instance.save()
        return Response({
            "success": True,
            "message": "Miembro del personal eliminado"
        })
