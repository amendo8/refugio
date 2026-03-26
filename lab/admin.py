from django.contrib import admin

from .models import ReparacionModulo, ReparacionModuloEstado, SmallPart, ConsumoSmallPart


class ConsumoSmallPartInline(admin.TabularInline):
    model = ConsumoSmallPart
    extra = 1
    readonly_fields = ('fecha_consumo',)


class ReparacionModuloEstadoInline(admin.TabularInline):
    model = ReparacionModuloEstado
    extra = 0
    readonly_fields = ('estado_anterior', 'estado_nuevo', 'tecnico', 'fecha_cambio', 'comentario', 'horas_hombre')
    can_delete = False


@admin.register(SmallPart)
class SmallPartAdmin(admin.ModelAdmin):
    list_display = ('numero_parte_sp', 'descripcion', 'stock_actual', 'precio_dolares')
    search_fields = ('numero_parte_sp', 'descripcion')


@admin.register(ReparacionModulo)
class ReparacionModuloAdmin(admin.ModelAdmin):
    list_display = (
        'parte_a_reparar',
        'estado_proceso',
        'tecnico_actual',
        'fecha_ingreso',
        'fecha_revision',
        'fecha_inicio_reparacion',
        'fecha_finalizacion',
        'fecha_irreparable',
        'horas_hombre_empleadas',
        'costo_final_laboratorio',
        'mostrar_dias_taller',
    )
    list_filter = ('estado_proceso', 'tecnico_actual')
    search_fields = ('parte_a_reparar__nombre_part', 'tecnico_actual__username')
    inlines = [ConsumoSmallPartInline, ReparacionModuloEstadoInline]
    readonly_fields = (
        'fecha_ingreso',
        'fecha_revision',
        'fecha_inicio_reparacion',
        'fecha_finalizacion',
        'fecha_irreparable',
        'mostrar_dias_taller',
        'costo_final_laboratorio',
    )

    def mostrar_dias_taller(self, obj):
        return obj.calcular_dias_habiles()

    mostrar_dias_taller.short_description = "Días Hábiles"
