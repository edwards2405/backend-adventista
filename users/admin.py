from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, Specialist, Cashier

# Registramos el modelo Role
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('nombre_rol', 'descripcion')

# Registramos el modelo User extendido
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('role',)}),
    )

@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'especialidad', 'cedula', 'user')
    search_fields = ('nombre_completo', 'cedula')

@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    list_display = ('nombre_empleado', 'telefono', 'user')
