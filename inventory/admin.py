from django.contrib import admin

# Register your models here.
from .models import Equipo, ParteModulo, Categoria

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('id_empresarial_unico', 'nombre_modelo', 'fabricante', 'categoria')
    search_fields = ('id_empresarial_unico', 'serial_fabricacion', 'nombre_modelo')
    list_filter = ('fabricante', 'categoria')

@admin.register(ParteModulo)
class ParteModuloAdmin(admin.ModelAdmin):
    list_display = ('nombre_part', 'numero_parte_fabricante', 'estado', 'stock_disponible', 'costo_actual')
    list_filter = ('estado', 'equipos_compatibles')
    search_fields = ('nombre_part', 'numero_parte_fabricante')
    filter_horizontal = ('equipos_compatibles',) # Facilita seleccionar múltiples equipos

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',) 

