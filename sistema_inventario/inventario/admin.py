from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm

from .models import (
    Empresa,
    Sucursal,
    Empleado,
    Computadora,
    Celular,
    HistorialAsignacion,
    
)

# =====================================================
# USER ADMIN – EMAIL OBLIGATORIO
# =====================================================
class CustomUserAdmin(UserAdmin):

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
            ),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.email:
            raise ValueError("El correo electrónico es obligatorio")
        super().save_model(request, obj, form, change)


# =====================================================
# EMPRESA
# =====================================================
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rfc', 'activo')
    search_fields = ('nombre', 'rfc')
    list_filter = ('activo',)


# =====================================================
# SUCURSAL
# =====================================================
@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'responsable')
    list_filter = ('empresa',)
    search_fields = ('nombre',)


# =====================================================
# EMPLEADO
# =====================================================
@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'numero_empleado',
        'empresa',
        'departamento',
        'supervisor',
        'fecha_ingreso'
    )
    list_filter = (
        'empresa', 
        'departamento',
        'clase',)
    
    search_fields = (
        'numero_empleado',
        'user__username',
        'user__email',
        'rfc',
        'curp'
    )

    autocomplete_fields = ('user', 'empresa')

    fieldsets = (
        ('Datos generales', {
            'fields': (
                'numero_empleado',
                'empresa',
                'clase',
                'departamento',
                'fecha_ingreso',
            )
        }),
        ('Datos personales', {
            'fields': (
                'rfc',
                'curp',
                'supervisor',
                'aprobador_gastos',
            )
        }),
        ('Acceso al sistema (opcional)', {
            'fields': ('user',),
            'description': 'Asigna un usuario solo si este empleado tendrá acceso al sistema.'
        }),
    )

    def nombre_empleado(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return "— Sin usuario —"
    nombre_empleado.short_description = "Empleado"

    def tiene_usuario(self, obj):
        return bool(obj.user)
    tiene_usuario.boolean = True
    tiene_usuario.short_description = "Acceso al sistema"


# =====================================================
# COMPUTADORAS – ADMIN INTELIGENTE
# =====================================================
@admin.register(Computadora)
class ComputadoraAdmin(admin.ModelAdmin):

    list_display = (
        'clave',
        'empleado',
        'marca',
        'modelo',
        'empresa',
        'sucursal',
        'estatus'
    )

    list_filter = ('empresa', 'sucursal', 'estatus', 'marca')
    search_fields = ('clave', 'service_tag')

    def has_change_permission(self, request, obj=None):
        # Permite ver y editar datos generales,
        # pero la asignación NO se toca aquí
        return True

# =====================================================
# CELULARES – ADMIN INTELIGENTE
# =====================================================
@admin.register(Celular)
class CelularAdmin(admin.ModelAdmin):

    list_display = (
        'marca',
        'modelo',
        'imei',
        'empleado',
        'empresa',
        'estatus'
    )

    list_filter = ('empresa', 'estatus', 'marca')
    search_fields = ('imei',)

    readonly_fields = (
        'empleado',
        'estatus'
    )

    def has_change_permission(self, request, obj=None):
        return True

# =========================
# FORM PERSONALIZADO
# =========================
class HistorialAsignacionAdminForm(ModelForm):
    class Meta:
        model = HistorialAsignacion
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        instance = HistorialAsignacion(**cleaned_data)

        try:
            instance.clean()
        except ValidationError as e:
            self.add_error(None, e)

        return cleaned_data


# =====================================================
# Hitorial de Asignaciones Admin
# =====================================================
@admin.register(HistorialAsignacion)
class HistorialAsignacionAdmin(admin.ModelAdmin):

    form = HistorialAsignacionAdminForm

    list_display = (
        'empleado',
        'empresa',
        'tipo_equipo',
        'equipo_asignado',
        'fecha_asignacion',
        'fecha_devolucion',
        'activo',
        'autorizado_por'
    )

    list_filter = (
        'empresa',
        'tipo_equipo',
        'activo',
        'fecha_asignacion'
    )

    search_fields = (
        'empleado__user__username',
        'empleado__numero_empleado',
        'autorizado_por',
        'computadora__clave',
        'celular__imei'
    )

    readonly_fields = (
        'empleado',
        'empresa',
        'tipo_equipo',
        'computadora',
        'celular',
        'fecha_asignacion'
    )

    fieldsets = (
        ('Empleado', {
            'fields': ('empleado', 'empresa')
        }),
        ('Equipo', {
            'fields': ('tipo_equipo', 'computadora', 'celular')
        }),
        ('Asignación', {
            'fields': (
                'fecha_asignacion',
                'fecha_devolucion',
                'activo',
                'autorizado_por',
                'observaciones'
            )
        }),
    )

    def equipo_asignado(self, obj):
        return obj.computadora or obj.celular

    equipo_asignado.short_description = "Equipo"

