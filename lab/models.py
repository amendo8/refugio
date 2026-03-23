from django.db import models

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

    def __str__(self): return f"{self.numero_parte_sp} - {self.descripcion}"




# 2. GESTIÓN DE REPARACIONES (Laboratorio y Control de Tiempos)
class ReparacionModulo(models.Model):
    ESTADOS_PROCESO = [
        ('RECIBIDO', 'Recibido / En Cola'),
        ('DIAGNOSTICO', 'En Diagnóstico'),
        ('ESPERA_PARTE', 'Pendiente por Small Parts (Faltante)'),
        ('EN_PROCESO', 'En Reparación Activa'),
        ('LISTO', 'Reparación Finalizada'),
        ('SIN_SOLUCION', 'No Reparable'),
    ]

    parte_a_reparar = models.ForeignKey('inventory.ParteModulo', on_delete=models.CASCADE)
    estado_proceso = models.CharField(max_length=15, choices=ESTADOS_PROCESO, default='RECIBIDO')
    
    # Control de Fechas
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    
    # Gestión de Cuellos de Botella
    insumos_faltantes_notas = models.TextField(blank=True, help_text="¿Qué correas o piezas faltan?")
    
    # Costeo
    horas_hombre_empleadas = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    valor_hh_aplicado = models.DecimalField(max_digits=6, decimal_places=2, default=25.00)
    
    componentes_usados = models.ManyToManyField(SmallPart, through='ConsumoSmallPart')

    def calcular_dias_habiles(self):
        """Calcula días de lunes a viernes en taller"""
        inicio = self.fecha_ingreso.date()
        fin = self.fecha_finalizacion.date() if self.fecha_finalizacion else datetime.date.today()
        dias = 0
        curr = inicio
        while curr <= fin:
            if curr.weekday() < 5: dias += 1
            curr += datetime.timedelta(days=1)
        return dias

    def costo_final_laboratorio(self):
        """Suma de Insumos + Labor"""
        insumos = sum(c.cantidad * c.small_part.precio_dolares for c in self.consumosmallpart_set.all())
        labor = self.horas_hombre_empleadas * self.valor_hh_aplicado
        return insumos + labor


# 3. TABLA DE CONSUMO (Relación Intermedia)
class ConsumoSmallPart(models.Model):
    reparacion = models.ForeignKey(ReparacionModulo, on_delete=models.CASCADE)
    small_part = models.ForeignKey(SmallPart, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()


