from django.contrib import admin
from .models import ConfiguracionSistema
# Register your models here.

@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ('valor_hora_hombre',)   
    search_fields = ('valor_hora_hombre',)
    