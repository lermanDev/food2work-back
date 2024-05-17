from django.db import models
from usuarios.models import Cliente, DireccionCliente, DireccionEmpresa
from comidas.models import ComponenteMenu


class LineaPedido(models.Model):
    raciones = models.IntegerField(default=1)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    direccion_cliente = models.ForeignKey(DireccionCliente, on_delete=models.CASCADE, blank=True, null=True)
    direccion_empresa = models.ForeignKey(DireccionEmpresa, on_delete=models.CASCADE, blank=True, null=True)
    menu = models.ForeignKey(ComponenteMenu, on_delete=models.CASCADE)
    facturado = models.BooleanField(default=False)

    def __str__(self):
        return self.cliente.user.email + ": " + str(self.raciones) + " " + self.menu.receta.nombre + " " + str(
            self.menu.menu.dia)
