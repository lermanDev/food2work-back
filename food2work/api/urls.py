from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^registro', views.crear_usuario),
    url(r'^recordar_contrasena', views.recuerda_contrasena),
    url(r'^get_usuario', views.get_usuario),
    url(r'^update_user', views.modifica_usuario),
    url(r'^change_password', views.modifica_password),
    url(r'^modifica_direccion', views.modifica_direccion),
    url(r'^delete_direccion', views.delete_direccion),
    url(r'^get_menus', views.get_menus),
    url(r'^crea_pedido', views.crea_pedido),
    url(r'^get_pedidos', views.get_pedidos),
    url(r'^borra_pedido', views.borra_pedido),

    # url(r'^factorial$', views.factorial),
]
