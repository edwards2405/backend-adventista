from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'name', 'title', 'avatar']

    def get_role(self, obj):
        # Si tiene rol asignado, lo retornamos, si no, uno por defecto
        return obj.role.nombre_rol if obj.role else 'superadmin' if obj.is_superuser else 'recepcion'

    def get_name(self, obj):
        if hasattr(obj, 'specialist_profile'):
            return obj.specialist_profile.nombre_completo
        if hasattr(obj, 'cashier_profile'):
            return obj.cashier_profile.nombre_empleado
        
        # Fallback al first_name / last_name nativo de Django
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username

    def get_title(self, obj):
        if hasattr(obj, 'specialist_profile'):
            return obj.specialist_profile.especialidad
        if hasattr(obj, 'cashier_profile'):
            return "Caja / Administrativo"
        if obj.is_superuser:
            return "Director General"
        return "Personal"

    def get_avatar(self, obj):
        name = self.get_name(obj)
        words = name.split()
        if len(words) >= 2:
            return f"{words[0][0]}{words[1][0]}".upper()
        elif len(words) == 1:
            return f"{words[0][:2]}".upper()
        return "UU"

class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class LoginResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    token = serializers.CharField()
    user = UserSerializer()

class StaffSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    since = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'status', 'since']

    def get_name(self, obj):
        # Usamos la misma lógica del UserSerializer
        if hasattr(obj, 'specialist_profile'):
            return obj.specialist_profile.nombre_completo
        if hasattr(obj, 'cashier_profile'):
            return obj.cashier_profile.nombre_empleado
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username

    def get_role(self, obj):
        return obj.role.nombre_rol if obj.role else 'superadmin' if obj.is_superuser else 'recepcion'

    def get_status(self, obj):
        return 'activo' if obj.is_active else 'inactivo'

    def get_since(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d') if obj.date_joined else None

class StaffStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['activo', 'inactivo'])

class StaffCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=['superadmin', 'recepcion', 'medico'])
    password = serializers.CharField(max_length=128, required=False, default='admin123')
