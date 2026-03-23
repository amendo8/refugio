from django.db import models
from django.utils import timezone

import datetime
import uuid

# Create your models here.

# 1. CATEGORÍAS (ATM, Máquina Fiscal, Contadora, etc.)
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

# 2. EQUIPOS / MODELOS (El "Host" o Máquina Principal)
class Equipo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    fabricante = models.CharField(max_length=100) # Ej: Wincor, Diebold, Glory
    nombre_modelo = models.CharField(max_length=100) # Ej: ProCash 2050xe, Cineo 2550
    serial_fabricacion = models.CharField(max_length=100, unique=True)
    id_empresarial_unico = models.CharField(max_length=100, unique=True) # ID Placa Interna
    precio_referencial = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    imagen = models.ImageField(upload_to='equipos/', null=True, blank=True)

    def __str__(self):
        return f"{self.id_empresarial_unico} - {self.nombre_modelo}"

# 3. PARTES / MÓDULOS (Compatibilidad Cruzada y Estados)
class ParteModulo(models.Model):
    ESTADO_CHOICES = [
        ('NUEVA', 'Nueva (Original)'),
        ('REPARADA', 'Reparada (Laboratorio)'),
        ('USADA', 'Usada (As-Is / Para Repara)'),
        ('SCRAP', 'Desecho / Canibalizada'),
    ]

    nombre_part = models.CharField(max_length=100) # Ej: Lectora IM330 USB, Stacker CMD-V4
    numero_parte_fabricante = models.CharField(max_length=100)
    
    # COMPATIBILIDAD: Una parte sirve para muchos modelos (Muchos a Muchos)
    equipos_compatibles = models.ManyToManyField(Equipo, related_name='partes_modulos')
    
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='USADA')
    costo_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    stock_disponible = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='partes_modulos/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_part} [{self.estado}] - P/N: {self.numero_parte_fabricante}"



