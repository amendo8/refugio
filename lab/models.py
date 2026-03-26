from django.conf import settings
from django.db import models
from django.utils import timezone

import datetime

# 1. SMALL PARTS (Insumos y Microcomponentes)
class SmallPart(models.Model):
    numero_parte_sp = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=200)
    fabricante_proveedor = models.CharField(max_length=100)
    precio_dolares = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.PositiveIntegerField(default=0)
    fecha_ingreso = models.DateField()
    imagen = models.ImageField(upload_to='small_parts/', null=True, blank=True)

    def __str__(self):
        return f"{self.numero_parte_sp} - {self.descripcion}"


# 2. GESTIÓN DE REPARACIONES (Laboratorio y Control de Tiempos)
class ReparacionModulo(models.Model):
    ESTADOS_PROCESO = [
        ('INGRESO', 'Ingreso'),
        ('REVISION', 'Revisión'),
        ('EN_PROCESO', 'En Proceso'),
        ('LISTO', 'Listo'),
        ('IRREPARABLE', 'Irreparable'),
    ]

    parte_a_reparar = models.ForeignKey('inventory.ParteModulo', on_delete=models.CASCADE)
    estado_proceso = models.CharField(max_length=15, choices=ESTADOS_PROCESO, default='INGRESO')

    # Control de Fechas del ciclo
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    fecha_inicio_reparacion = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    fecha_irreparable = models.DateTimeField(null=True, blank=True)

    tecnico_actual = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reparaciones_asignadas')
    insumos_faltantes_notas = models.TextField(blank=True, help_text="¿Qué correas o piezas faltan?")

    horas_hombre_empleadas = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    valor_hh_aplicado = models.DecimalField(max_digits=8, decimal_places=2, default=25.00)

    componentes_usados = models.ManyToManyField(SmallPart, through='ConsumoSmallPart')

    

    def calcular_dias_habiles(self):
        inicio = self.fecha_ingreso.date()
        fin = self.fecha_finalizacion.date() if self.fecha_finalizacion else datetime.date.today()
        dias = 0
        curr = inicio
        while curr <= fin:
            if curr.weekday() < 5:
                dias += 1
            curr += datetime.timedelta(days=1)
        return dias

    def costo_total_insumos(self):
        return sum(c.cantidad * c.small_part.precio_dolares for c in self.consumosmallpart_set.all())

    def costo_total_labor(self):
        return self.horas_hombre_empleadas * self.valor_hh_aplicado

    def costo_final_laboratorio(self):
        return self.costo_total_insumos() + self.costo_total_labor()

    def total_horas_historial(self):
        return self.estadocambio_set.aggregate(total=models.Sum('horas_hombre')).get('total') or 0

    def total_cantidad_consumo(self):
        return self.consumosmallpart_set.aggregate(total=models.Sum('cantidad')).get('total') or 0

    def save(self, *args, **kwargs):
        prev_estado = None
        if self.pk:
            try:
                prev = ReparacionModulo.objects.get(pk=self.pk)
                prev_estado = prev.estado_proceso
            except ReparacionModulo.DoesNotExist:
                prev_estado = None

        super().save(*args, **kwargs)

        if prev_estado and prev_estado != self.estado_proceso:
            ReparacionModuloEstado.objects.create(
                reparacion=self,
                estado_anterior=prev_estado,
                estado_nuevo=self.estado_proceso,
                tecnico=self.tecnico_actual,
                fecha_cambio=timezone.now(),
                comentario=f"Transición {prev_estado} -> {self.estado_proceso}",
                horas_hombre=0,
            )

        if self.estado_proceso == 'REVISION' and not self.fecha_revision:
            self.fecha_revision = timezone.now()
            super().save(update_fields=['fecha_revision'])

        if self.estado_proceso == 'EN_PROCESO' and not self.fecha_inicio_reparacion:
            self.fecha_inicio_reparacion = timezone.now()
            super().save(update_fields=['fecha_inicio_reparacion'])

        if self.estado_proceso == 'LISTO' and not self.fecha_finalizacion:
            self.fecha_finalizacion = timezone.now()
            super().save(update_fields=['fecha_finalizacion'])

        if self.estado_proceso == 'IRREPARABLE' and not self.fecha_irreparable:
            self.fecha_irreparable = timezone.now()
            super().save(update_fields=['fecha_irreparable'])
    
    def __str__(self):
        return f"Reparación #{self.pk} - {self.parte_a_reparar} ({self.get_estado_proceso_display()})"

class ReparacionModuloEstado(models.Model):
    reparacion = models.ForeignKey(ReparacionModulo, on_delete=models.CASCADE, related_name='estadocambio_set')
    estado_anterior = models.CharField(max_length=15, choices=ReparacionModulo.ESTADOS_PROCESO)
    estado_nuevo = models.CharField(max_length=15, choices=ReparacionModulo.ESTADOS_PROCESO)
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True)
    horas_hombre = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f"{self.reparacion} {self.get_estado_anterior_display()} -> {self.get_estado_nuevo_display()} ({self.fecha_cambio:%Y-%m-%d %H:%M})"


# 3. TABLA DE CONSUMO (Relación Intermedia)
class ConsumoSmallPart(models.Model):
    reparacion = models.ForeignKey(ReparacionModulo, on_delete=models.CASCADE)
    small_part = models.ForeignKey(SmallPart, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_consumo = models.DateTimeField(auto_now_add=True)
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if self.cantidad > 0 and self.small_part.stock_actual >= self.cantidad:
            self.small_part.stock_actual = models.F('stock_actual') - self.cantidad
            self.small_part.save(update_fields=['stock_actual'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad}x {self.small_part} para {self.reparacion}"


