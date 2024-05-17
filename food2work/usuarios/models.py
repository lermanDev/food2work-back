from django.db import models
from django.contrib.auth.models import User


class EmpresaComida(models.Model):
    nombre_empresa = models.CharField('Nombre Empresa', max_length=100, default='')
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    cp_list = models.TextField("Listado Codigos postales disponibles", default='[]')

    def __str__(self):
        return self.nombre_empresa


class Empresa(models.Model):
    nombre_empresa = models.CharField('Nombre Empresa', max_length=100, default='')
    id_empresa = models.CharField('Id Empresa', max_length=100, default='')
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.nombre_empresa


class Cliente(models.Model):
    OPCIONES_PAGO = (
        ("TARJETA", "Pago con tarjeta al recoger el pedido"),
        ("EFECTIVO", "Pago en efectivo al recoger el pedido"),
    )

    TARJETA = 'TARJETA'
    EFECT = 'EFECTIVO'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    id_empresa = models.ForeignKey(Empresa, related_name='Empresa', on_delete=models.SET_NULL, null=True, blank=True)
    notificaciones = models.BooleanField(default=True)
    metodo_pago = models.CharField(
        max_length=30,
        choices=OPCIONES_PAGO,
        default=EFECT,
    )
    direccion_defecto = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email


class DireccionCliente(models.Model):
    nombre_direccion = models.CharField('Nombre Direccion', max_length=50)
    telefono = models.CharField('Teléfono', max_length=9)
    ciudad = models.CharField('Ciudad', max_length=200)
    direccion = models.CharField("Dirección", max_length=1024)
    anotaciones = models.CharField("Dirección", max_length=1024)
    codigo_postal = models.CharField("Código Postal", max_length=12)
    modificable = models.BooleanField(default=True)
    cliente = models.ForeignKey(Cliente, related_name='direcciones_cliente', on_delete=models.CASCADE)


class DireccionEmpresa(models.Model):
    nombre_direccion = models.CharField('Nombre Direccion', max_length=50)
    telefono = models.CharField('Teléfono', max_length=9)
    ciudad = models.CharField('Ciudad', max_length=200)
    direccion = models.CharField("Dirección", max_length=1024)
    anotaciones = models.CharField("Información Extra", max_length=1024)
    codigo_postal = models.CharField("Código Postal", max_length=12)
    modificable = models.BooleanField(default=False)
    cliente = models.OneToOneField(Empresa, related_name='direccion_empresa', on_delete=models.CASCADE)
