from django.contrib import admin

from .models import ReparacionModulo, SmallPart, ConsumoSmallPart
# Register your models here.
@admin.register(SmallPart)
class SmallPartAdmin(admin.ModelAdmin):
    list_display = ('numero_parte_sp', 'descripcion', 'fabricante_proveedor', 'precio_dolares', 'stock_actual', 'fecha_ingreso')
    search_fields = ('numero_parte_sp', 'descripcion', 'fabricante_proveedor')
    list_filter = ('fabricante_proveedor',)

@admin.register(ReparacionModulo)
class ReparacionModuloAdmin(admin.ModelAdmin):
    list_display = ('parte_a_reparar', 'estado_proceso', 'fecha_ingreso', 'fecha_finalizacion', 'horas_hombre_empleadas', 'valor_hh_aplicado')
    search_fields = ('parte_a_reparar__nombre_part',)
    list_filter = ('estado_proceso',)

@admin.register(ConsumoSmallPart)
class ConsumoSmallPartAdmin(admin.ModelAdmin):  
    list_display = ('reparacion', 'small_part', 'cantidad')
    search_fields = ('reparacion__parte_a_reparar__nombre_part', 'small_part__numero_parte_sp')
    list_filter = ('small_part__fabricante_proveedor',)

