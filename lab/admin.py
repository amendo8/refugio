from django.contrib import admin

from .models import ReparacionModulo, SmallPart, ConsumoSmallPart
# Register your models here.

class ConsumoSmallPartInline(admin.TabularInline):
    model = ConsumoSmallPart
    extra = 1  # Cuántas filas vacías mostrar por defecto


@admin.register(SmallPart)
class SmallPartAdmin(admin.ModelAdmin):
    list_display = ('numero_parte_sp', 'descripcion', 'stock_actual', 'precio_dolares')
    search_fields = ('numero_parte_sp', 'descripcion')

@admin.register(ReparacionModulo)
class ReparacionModuloAdmin(admin.ModelAdmin):
    list_display = ('parte_a_reparar', 'estado_proceso', 'fecha_ingreso',   'dias_taller')
    inlines = [ConsumoSmallPartInline]
    search_fields = ('parte_a_reparar__nombre_part',)
    list_filter = ('estado_proceso',)

    # Esta función resuelve el error E108
    def mostrar_dias_taller(self, obj):
        return obj.calcular_dias_habiles()
    
    # Esto le pone el título a la columna en el Admin
    mostrar_dias_taller.short_description = "Días Hábiles"
    
    # Esto le pone el título a la columna en el Admin
    mostrar_dias_taller.short_description = "Días Hábiles"

