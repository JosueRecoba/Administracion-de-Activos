from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


# =========================
# EMPRESA
# =========================
class Empresa(models.Model):
    nombre = models.CharField(max_length=150)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    contacto = models.CharField(max_length=150, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# =========================
# SUCURSAL
# =========================
class Sucursal(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="sucursales")
    nombre = models.CharField(max_length=100) 
    direccion = models.TextField(blank=True, null=True)
    responsable = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.empresa.nombre} - {self.nombre}"


# =========================
# BASE INVENTARIO (ABSTRACT)
# =========================
class InventarioBase(models.Model):
    ESTATUS_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('BAJA', 'Baja'),
        ('REPARACION', 'En reparación'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    usuario = models.CharField(max_length=150)
    puesto = models.CharField(max_length=100, blank=True, null=True)
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='ACTIVO')
    comentarios = models.TextField(blank=True, null=True)

    fecha_alta = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


# =========================
# COMPUTADORAS
# =========================
class Computadora(InventarioBase):

    TIPO_EQUIPO = [
        ('LAPTOP', 'Laptop'),
        ('DESKTOP', 'Desktop'),
    ]

    TIPO_DD = [
        ('HDD', 'HDD'),
        ('SSD', 'SSD'),
        ('NVME', 'NVMe'),
    ]

    empleado = models.OneToOneField(
        'Empleado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='computadora'
    )

    clave = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_EQUIPO)
    nombre_equipo = models.CharField(max_length=150)

    antivirus = models.CharField(max_length=100, blank=True, null=True)
    fecha_compra = models.DateField(blank=True, null=True)

    service_tag = models.CharField(max_length=100, blank=True, null=True)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)

    procesador = models.CharField(max_length=150)
    mac_address = models.CharField(max_length=50, blank=True, null=True)

    ram = models.CharField(max_length=50)
    tipo_dd = models.CharField(max_length=20, choices=TIPO_DD)
    capacidad_dd = models.CharField(max_length=50)

    sistema_operativo = models.CharField(max_length=100)
    office_version = models.CharField(max_length=50, blank=True, null=True)
    clave_licencia_office = models.CharField(max_length=100, blank=True, null=True)
    correo_office = models.EmailField(blank=True, null=True)

    monitor = models.BooleanField(default=False)
    service_tag_monitor = models.CharField(max_length=100, blank=True, null=True)

    nobreak = models.BooleanField(default=False)
    perifericos = models.TextField(blank=True, null=True)

    vale_resguardo = models.CharField(max_length=100, blank=True, null=True)
    renovacion = models.CharField(max_length=50, blank=True, null=True)

    # PDFs
    resguardo_pdf_generado = models.FileField(
        upload_to='resguardos/generados/',
        blank=True,
        null=True
    )

    resguardo_pdf_firmado = models.FileField(
        upload_to='resguardos/firmados/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.clave} - {self.empleado}"


# =========================
# CELULARES
# =========================
class Celular(InventarioBase):

    empleado = models.OneToOneField(
        'Empleado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='celular'
    )

    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    imei = models.CharField(max_length=50, unique=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    sistema_operativo = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.empleado}"

# =========================
# PERFIL DE EMPLEADO
# =========================
class Empleado(models.Model):

    CLASE_CHOICES = [
        ('EBU', 'EBU'),
        ('INTERNO', 'Interno'),
        ('EXTERNO', 'Externo'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='empleado'

    )

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='empleados'
    )

    numero_empleado = models.CharField(max_length=20, unique=True)

    rfc = models.CharField(max_length=13, unique=True)
    curp = models.CharField(max_length=18, unique=True)


    clase = models.CharField(max_length=20, choices=CLASE_CHOICES)

    departamento = models.CharField(max_length=100)

    supervisor = models.CharField(max_length=150)
    aprobador_gastos = models.CharField(max_length=150)

    fecha_ingreso = models.DateField()

    estatus_equipo = models.CharField(
    max_length=20,
    choices=[
        ('SIN_EQUIPO', 'Sin equipo'),
        ('CON_EQUIPO', 'Con equipo'),
    ],
    default='SIN_EQUIPO'
)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.numero_empleado}"


# =========================
# Historial de Asignacion
# =========================   
class HistorialAsignacion(models.Model):

    TIPO_EQUIPO_CHOICES = [
        ('COMPUTADORA', 'Computadora'),
        ('CELULAR', 'Celular'),
    ]

    empleado = models.ForeignKey(
        'Empleado',
        on_delete=models.PROTECT,
        related_name='historial_asignaciones'
    )

    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.PROTECT,
        related_name='historial_asignaciones'
    )

    tipo_equipo = models.CharField(
        max_length=20,
        choices=TIPO_EQUIPO_CHOICES
    )

    computadora = models.ForeignKey(
        'Computadora',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    celular = models.ForeignKey(
        'Celular',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    fecha_asignacion = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)

    autorizado_por = models.CharField(
        max_length=150,
        help_text="Nombre de quien autorizó la asignación o devolución"
    )

    activo = models.BooleanField(default=True)

    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Historial de asignación"
        verbose_name_plural = "Historial de asignaciones"
        ordering = ['-fecha_asignacion']

    def clean(self):
        # 1️ El empleado debe pertenecer a la empresa
        if self.empleado.empresa != self.empresa:
            raise ValidationError(
                "La empresa del empleado no coincide con la asignación."
            )

        # 2️ Validar tipo de equipo
        if self.tipo_equipo == 'COMPUTADORA' and not self.computadora:
            raise ValidationError("Debes seleccionar una computadora.")

        if self.tipo_equipo == 'CELULAR' and not self.celular:
            raise ValidationError("Debes seleccionar un celular.")

        # 3️ El equipo debe pertenecer a la empresa
        if self.computadora and self.computadora.empresa != self.empresa:
            raise ValidationError("La computadora no pertenece a esta empresa.")

        if self.celular and self.celular.empresa != self.empresa:
            raise ValidationError("El celular no pertenece a esta empresa.")

        # 4️ El equipo no debe estar ya asignado
        if self.computadora and self.computadora.estatus == 'ASIGNADO':
            raise ValidationError("Esta computadora ya está asignada.")

        if self.celular and self.celular.estatus == 'ASIGNADO':
            raise ValidationError("Este celular ya está asignado.")

    def save(self, *args, **kwargs):
        # Ejecutar validaciones
        self.full_clean()

        # 1️ Cerrar asignaciones activas previas del mismo tipo
        asignaciones_previas = HistorialAsignacion.objects.filter(
            empleado=self.empleado,
            tipo_equipo=self.tipo_equipo,
            activo=True
        )

        for asignacion in asignaciones_previas:
            asignacion.activo = False
            asignacion.fecha_devolucion = timezone.now()
            asignacion.save()

            # Liberar equipo anterior
            if asignacion.computadora:
                asignacion.computadora.estatus = 'DISPONIBLE'
                asignacion.computadora.save()

            if asignacion.celular:
                asignacion.celular.estatus = 'DISPONIBLE'
                asignacion.celular.save()

        # 2️ Marcar nuevo equipo como asignado
        if self.computadora:
            self.computadora.estatus = 'ASIGNADO'
            self.computadora.save()

        if self.celular:
            self.celular.estatus = 'ASIGNADO'
            self.celular.save()

        super().save(*args, **kwargs)

    def __str__(self):
        equipo = self.computadora or self.celular
        return f"{self.empleado} - {equipo}"