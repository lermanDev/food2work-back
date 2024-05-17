from django.contrib import admin
from ingredientes.models import Ingrediente, DatoNutricional, InfoNutricional

# Register your models here.
admin.site.register(Ingrediente)
admin.site.register(DatoNutricional)
admin.site.register(InfoNutricional)
