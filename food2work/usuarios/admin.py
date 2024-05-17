from django.contrib import admin
from usuarios.models import Empresa, DireccionCliente, DireccionEmpresa, Cliente, EmpresaComida
# Register your models here.
admin.site.register(EmpresaComida)
admin.site.register(Empresa)
admin.site.register(DireccionEmpresa)
admin.site.register(Cliente)
admin.site.register(DireccionCliente)
