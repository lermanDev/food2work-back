from django.db import models
from ingredientes.models import Ingrediente
from usuarios.models import EmpresaComida


class Categoria(models.Model):
    nombre = models.CharField(max_length=128)

    def __str__(self):
        return self.nombre


class Alergeno(models.Model):
    nombre = models.CharField(max_length=128)
    icono = models.CharField(max_length=128)
    color = models.CharField(max_length=128)
    libreria = models.CharField(max_length=128)

    def __str__(self):
        return self.nombre


class Receta(models.Model):
    nombre = models.CharField(max_length=128)
    raciones = models.IntegerField(default=1)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    empresa = models.ForeignKey(EmpresaComida, on_delete=models.DO_NOTHING)
    descripcion = models.TextField(default="")
    imagen = models.ImageField(upload_to='imagenes/recetas/', null=True, blank=True)
    peso_porcion = models.IntegerField(default=100)
    alergenos = models.ManyToManyField(Alergeno, null=True, blank=True)

    def __str__(self):
        return self.nombre+' ('+str(self.raciones)+'r.)'


class Menu(models.Model):
    nombre = models.CharField(max_length=100)
    empresa = models.ForeignKey(EmpresaComida, on_delete=models.CASCADE)
    dia = models.DateField()

    def __str__(self):
        return self.nombre


class Componente(models.Model):  # componentes de la receta
    receta = models.ForeignKey(Receta, related_name='componentes', on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.FloatField()

    def __str__(self):
        return self.receta.nombre+' ('+self.ingrediente.nombre+')'


class ComponenteMenu(models.Model):  # las recetas del menu
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='componentes_menu')
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    precio = models.DecimalField(decimal_places=2, max_digits=4, default=3.5, editable=True)
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.receta.nombre+' ('+self.menu.nombre+')' + " " + self.receta.nombre + " " + str(self.precio) + "€"
