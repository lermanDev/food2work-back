from django.contrib import admin
from comidas.models import Categoria, Receta, Menu, Componente, ComponenteMenu, Alergeno

# Register your models here.
admin.site.register(Categoria)
admin.site.register(Receta)
admin.site.register(Menu)
admin.site.register(Componente)
admin.site.register(ComponenteMenu)
admin.site.register(Alergeno)
