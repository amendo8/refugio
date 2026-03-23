from django.db import models


#  CONFIGURACIÓN GLOBAL (Hora-Hombre)
class ConfiguracionSistema(models.Model):
    valor_hora_hombre = models.DecimalField(max_digits=6, decimal_places=2, default=25.00)



