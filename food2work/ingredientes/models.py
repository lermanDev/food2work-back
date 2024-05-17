from django.db import models


class Ingrediente(models.Model):
    nombre = models.CharField(max_length=128)
    unidad = models.CharField(max_length=20)  # g, l, k normalmente es g
    equivalencia_en_gramos = models.FloatField(default=100)  # normalmente 1

    def __str__(self):
        return self.nombre + ' (' + self.unidad + ')'


class DatoNutricional(models.Model):
    nombre = models.CharField(max_length=128)
    tipo = models.CharField(max_length=20)
    unidad = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre + ' (' + self.unidad + ')'


class InfoNutricional(models.Model):
    ingrediente = models.ForeignKey(Ingrediente, related_name='datos_nutricionales', on_delete=models.CASCADE)
    dato_nutricional = models.ForeignKey(DatoNutricional, on_delete=models.CASCADE)
    valor = models.FloatField()  # cuanto es el valor
    cantidad = models.FloatField()  # cantidad de ingrediente por la que tiene valor

    def __str__(self):
        return self.ingrediente.nombre + ' x ' + str(
            self.cantidad) + self.ingrediente.unidad + ' ' + self.dato_nutricional.nombre + ': ' + str(
            self.valor) + self.dato_nutricional.unidad
