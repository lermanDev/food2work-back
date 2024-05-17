from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.views import APIView
from rest_framework import status
import time
from django.contrib.auth.models import User
from usuarios.models import Cliente, Empresa, DireccionCliente, DireccionEmpresa
from comidas.models import Menu, ComponenteMenu, Receta, Componente
from ingredientes.models import InfoNutricional, Ingrediente, DatoNutricional
from pedidos.models import LineaPedido
from django.db import IntegrityError
from django.contrib.auth.models import Group
from django.core import serializers
import datetime


# Create your views here.
class EsUsuario(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='usuario').exists():
            return True
        else:
            return False


@api_view(['POST'])
def recuerda_contrasena(request):
    from django.core.mail import send_mail

    try:
        email = request.POST['email']

        user = User.objects.get(username__exact=email, groups__name='usuario')
        password = User.objects.make_random_password()

        user.set_password(password)
        user.save()

        res = send_mail(
            'Regenerarción contraseña food2work',
            'Hemos regenerado tu contraseña, puedes iniciar sesión usando la siguiente: ' + password +
            ' Recuerda cambiarla al iniciar sesión ',
            'csgolerman@gmail.com',
            [email],
            fail_silently=False,
            html_message='<p>Hemos regenerado tu contraseña, puedes iniciar sesión usando la siguiente: <strong>' + password +
                         '</strong>  </p> <p>Recuerda cambiarla al iniciar sesión</p>',
        )

        return Response({"success": " Contraseña regenerada correctamente "}, status=status.HTTP_202_ACCEPTED)
    except User.DoesNotExist as e:
        return Response({"error": " Correo electrónico no valido "},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e) + " " + str(request.POST)},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def crear_usuario(request):
    try:
        grupo_usuario = Group.objects.get(name='usuario')

        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        password = request.POST['password']
        email = request.POST['email']
        id_empresa = request.POST['id_empresa']

        if email and nombre and apellido and email and password:
            if id_empresa:
                try:
                    empresa = Empresa.objects.get(id_empresa=id_empresa)

                    usuario = User.objects.create_user(username=email, first_name=nombre, last_name=apellido,
                                                       email=email,
                                                       password=password)
                    cliente = Cliente(user=usuario)

                    cliente.id_empresa = empresa
                    usuario.save()

                    usuario.groups.add(grupo_usuario)

                    cliente.save()

                except Empresa.DoesNotExist as e:
                    return Response({"error": "No existe ninguna empresa asociada a ese código"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                usuario = User.objects.create_user(username=email, first_name=nombre, last_name=apellido,
                                                   email=email,
                                                   password=password)
                cliente = Cliente(user=usuario)
                usuario.save()

                usuario.groups.add(grupo_usuario)

                cliente.save()

            return Response({"success": "Usuario creado correctamente "}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Faltan datos necesarios, comprueba todos los campos"},
                            status=status.HTTP_400_BAD_REQUEST)
    # except KeyError as e:
    #     return Response({"error": str(e.args[0]) + " es necesario"}, status=status.HTTP_400_BAD_REQUEST)
    #     print()
    except IntegrityError as e:
        return Response({"error": "Ya existe un usario creado con este correo, intenta recuperar tu contraseña"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e) + " " + str(request.POST)},
                        status=status.HTTP_400_BAD_REQUEST)  # , "received": str(request.POST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def get_usuario(request):
    try:
        cliente = Cliente.objects.get(user=request.user)

        metodo_pago_posibles = cliente.OPCIONES_PAGO  # cliente.get_metodo_pago_display()

        # direcciones =
        direcciones = DireccionCliente.objects.filter(cliente=cliente).values()

        empresa_info = {}
        id_empresa = ""
        if cliente.id_empresa and cliente.id_empresa.id_empresa is not None:
            empresa = Empresa.objects.get(id_empresa=cliente.id_empresa.id_empresa)
            empresa_info = DireccionEmpresa.objects.filter(cliente=empresa).values()
            id_empresa = cliente.id_empresa.id_empresa

        respuesta = {
            "correo": request.user.email,
            "nombre": request.user.first_name,
            "apellido": request.user.last_name,
            "id_empresa": id_empresa,
            "empresa_info": empresa_info,
            "notificaciones": cliente.notificaciones,

            "metodo_pago": [cliente.metodo_pago, cliente.get_metodo_pago_display()],
            "metodo_pago_posibles": metodo_pago_posibles,

            "direccion_defecto": cliente.direccion_defecto,
            "direcciones": direcciones,
        }
        return Response({"success": respuesta}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def modifica_usuario(request):
    try:
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        id_empresa = request.POST['id_empresa']
        notificaciones = request.POST['notificaciones']
        metodo_pago = request.POST['metodo_pago']
        direccion_defecto = request.POST['direccion_defecto']

        user = request.user
        cliente = Cliente.objects.get(user=user)

        if nombre != '':
            user.first_name = nombre
        if apellido != '':
            user.last_name = apellido

        if notificaciones != '':
            cliente.notificaciones = True if notificaciones == 'true' else False

        if metodo_pago != '':
            cliente.metodo_pago = metodo_pago

        if id_empresa != '':
            try:
                empresa = Empresa.objects.get(id_empresa=id_empresa)
                cliente.id_empresa = empresa
            except Empresa.DoesNotExist as e:
                return Response({"error": "No existe ninguna empresa con ese ID"}, status=status.HTTP_400_BAD_REQUEST)

        if direccion_defecto != '':
            if direccion_defecto != '0':  # si es 0 por defecto es la de la empresa
                direccion = DireccionCliente.objects.get(id=direccion_defecto)
                cliente.direccion_defecto = direccion.id
            else:
                cliente.direccion_defecto = 0

        cliente.save()
        user.save()

        return Response({"success": "Usuario actualizado correctamente"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def modifica_password(request):
    from django.contrib.auth import authenticate

    try:
        usuario = request.POST['usuario']

        if request.user.username == usuario:

            old_password = request.POST['old_password']
            new_password = request.POST['new_password']

            # Verificamos las credenciales del usuario
            usuario = authenticate(username=usuario, password=old_password)

            if usuario is not None:
                usuario.set_password(new_password)
                usuario.save()
                return Response({"success": "Usuario actualizado correctamente"}, status=status.HTTP_200_OK)

        return Response({"error": "Algo ha ido mal, comprueba los datos introducidos"},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def modifica_direccion(request):
    try:
        id_direccion = request.POST['id_direccion']

        nombre_direccion = request.POST['nombre_direccion']
        telefono = request.POST['telefono']
        ciudad = request.POST['ciudad']
        direccion = request.POST['direccion']
        anotaciones = request.POST['anotaciones']
        codigo_postal = request.POST['codigo_postal']

        user = request.user
        cliente = Cliente.objects.get(user=user)

        if id_direccion and id_direccion != "" and direccion != 'undefined':  # debemos actualizar
            direccion_cliente = DireccionCliente.objects.get(id=id_direccion, cliente=cliente)
            direccion_cliente.nombre_direccion = nombre_direccion
            direccion_cliente.telefono = telefono
            direccion_cliente.ciudad = ciudad
            direccion_cliente.direccion = direccion
            direccion_cliente.anotaciones = anotaciones
            direccion_cliente.codigo_postal = codigo_postal
            direccion_cliente.save()

            return Response({"success": "Dirección actualizada correctamente"}, status=status.HTTP_200_OK)
        else:  # debemos crear
            direccion_cliente = DireccionCliente(nombre_direccion=nombre_direccion, telefono=telefono,
                                                 ciudad=ciudad, direccion=direccion,
                                                 anotaciones=anotaciones, codigo_postal=codigo_postal, cliente=cliente)

            direccion_cliente.save()
            return Response({"success": "Dirección creada correctamente"}, status=status.HTTP_200_OK)

        # return Response({"error": "Algo ha ido mal, comprueba los datos introducidos"},
        #                 status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e) + request.POST['id_direccion']}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def delete_direccion(request):
    try:
        id_direccion = request.POST['id_direccion']
        user = request.user
        cliente = Cliente.objects.get(user=user)

        if id_direccion and id_direccion != "":  # debemos actualizar
            direccion_cliente = DireccionCliente.objects.get(id=id_direccion, cliente=cliente)

            if str(cliente.direccion_defecto) == id_direccion:
                cliente.direccion_defecto = 0
                cliente.save()

            direccion_cliente.delete()

            return Response({"success": "Dirección borrada correctamente"}, status=status.HTTP_200_OK)

        return Response({"error": "Algo ha ido mal, comprueba los datos introducidos"},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def get_menus(request):
    # tenemos que obtener los platos que puede comprar ese cliente ese día
    # tenemos que filtrar por la direccion que el cliente pida los platos disponibles
    try:
        user = request.user
        cliente = Cliente.objects.get(user=user)
        dia = request.POST['fecha_pedido']
        id_direccion = request.POST['id_direccion']
        if 'texto_buscar' in request.POST:
            texto_buscar = request.POST['texto_buscar']
        else:
            texto_buscar = ""

        if id_direccion and dia and cliente:
            if id_direccion == '0':
                empresa = Empresa.objects.get(id_empresa=cliente.id_empresa.id_empresa)
                direccion = DireccionEmpresa.objects.get(cliente=empresa)
            else:
                direccion = DireccionCliente.objects.get(id=id_direccion, cliente=cliente)
            # menus_postres = Menu.objects.filter(dia=str(dia), empresa__cp_list__contains=)

            if texto_buscar:
                menus_disponibles = ComponenteMenu.objects.filter(menu__dia=str(dia),
                                                                  menu__empresa__cp_list__contains=direccion.codigo_postal,
                                                                  receta__nombre__icontains=texto_buscar)
            else:
                menus_disponibles = ComponenteMenu.objects.filter(menu__dia=str(dia),
                                                                  menu__empresa__cp_list__contains=direccion.codigo_postal)

            # {'id': 1, 'receta__categoria__nombre': 'PLATOS', 'receta__nombre': 'PAELLA VALENCIANA',
            #  'receta__imagen': 'imagenes/recetas/paella-valenciana.jpg', 'precio': Decimal('3.5')}

            menus = {
                "PLATOS": [],
                "ENSALADAS": [],
                "TAPAS": [],
                "BEBIDAS": [],
                "POSTRES": [],
            }

            menus_buscar = []

            for menu in menus_disponibles:
                componentes = Componente.objects.filter(receta_id=menu.receta.id)
                lista_ingredientes = []
                valores_nutricionales = {}
                for componente in componentes:
                    # componente.cantidad son los gramos de ingrediente que contiene
                    # info_nutricional.valor es el valor por cada 100 gramos
                    # debemos dividir la cantidad entre 100 y multiplicar por info_nutricional.valor

                    lista_ingredientes.append(componente.ingrediente.nombre)
                    # AHORA TENEMOS QUE OBTENER LOS DATOS NUTRICIONALES POR CADA INGREDIENTE Y SUMARLOS TODOS
                    infos_nutricionales = InfoNutricional.objects.filter(ingrediente=componente.ingrediente)
                    for info_nutricional in infos_nutricionales:
                        if info_nutricional.dato_nutricional.tipo not in valores_nutricionales:
                            valores_nutricionales[info_nutricional.dato_nutricional.tipo] = {}
                            if info_nutricional.dato_nutricional.nombre not in valores_nutricionales[
                                info_nutricional.dato_nutricional.tipo]:
                                valores_nutricionales[info_nutricional.dato_nutricional.tipo][
                                    info_nutricional.dato_nutricional.nombre] = (
                                        (componente.cantidad / 100) * info_nutricional.valor)
                            else:
                                valores_nutricionales[info_nutricional.dato_nutricional.tipo][
                                    info_nutricional.dato_nutricional.nombre] += (
                                        (componente.cantidad / 100) * info_nutricional.valor)
                        else:
                            if info_nutricional.dato_nutricional.nombre not in valores_nutricionales[
                                info_nutricional.dato_nutricional.tipo]:
                                valores_nutricionales[info_nutricional.dato_nutricional.tipo][
                                    info_nutricional.dato_nutricional.nombre] = (
                                        (componente.cantidad / 100) * info_nutricional.valor)
                            else:
                                valores_nutricionales[info_nutricional.dato_nutricional.tipo][
                                    info_nutricional.dato_nutricional.nombre] += (
                                        (componente.cantidad / 100) * info_nutricional.valor)

                valores_nutricionales_aux = {}
                for clave_categoria in valores_nutricionales:
                    for nombre_valor in valores_nutricionales[clave_categoria]:
                        calorias_aux = ""
                        nombre_valor_aux = DatoNutricional.objects.get(nombre=nombre_valor)
                        if nombre_valor_aux.nombre == 'energía, total':
                            calorias_aux = "/" + str(
                                round(valores_nutricionales[clave_categoria][nombre_valor] * 0.2388, 2)) + " kcal"

                        if clave_categoria not in valores_nutricionales_aux:
                            valores_nutricionales_aux[clave_categoria] = {}
                            if nombre_valor not in valores_nutricionales_aux[clave_categoria]:
                                valores_nutricionales_aux[clave_categoria][nombre_valor] = str(
                                    round(valores_nutricionales[clave_categoria][nombre_valor],
                                          2)) + " " + nombre_valor_aux.unidad + calorias_aux
                            else:
                                valores_nutricionales_aux[clave_categoria][nombre_valor] = str(
                                    round(valores_nutricionales[clave_categoria][nombre_valor],
                                          2)) + " " + nombre_valor_aux.unidad + calorias_aux
                        else:
                            if nombre_valor not in valores_nutricionales_aux[clave_categoria]:
                                valores_nutricionales_aux[clave_categoria][nombre_valor] = str(
                                    round(valores_nutricionales[clave_categoria][nombre_valor],
                                          2)) + " " + nombre_valor_aux.unidad + calorias_aux
                            else:
                                valores_nutricionales_aux[clave_categoria][nombre_valor] = str(
                                    round(valores_nutricionales[clave_categoria][nombre_valor],
                                          2)) + " " + nombre_valor_aux.unidad + calorias_aux

                alergenos = []

                for alergeno in menu.receta.alergenos.all():
                    listado = {
                        "nombre": alergeno.nombre,
                        "icono": alergeno.icono,
                        "color": alergeno.color,
                        "libreria": alergeno.libreria,
                    }
                    alergenos.append(listado)

                # 'id', 'receta__categoria__nombre', 'receta__nombre', 'receta__imagen', 'precio', 'receta__componentes__ingrediente_id', 'receta')
                plato = {
                    "id_componente_menu": menu.id,
                    "descripcion": menu.receta.descripcion,
                    "nombre_receta": menu.receta.nombre,
                    "peso": menu.receta.peso_porcion,
                    "imagen_receta": menu.receta.imagen.url if menu.receta.imagen else "",
                    "precio": float(menu.precio),
                    "lista_ingredientes": lista_ingredientes,
                    "alergenos": alergenos,
                    "valores_nutricionales": valores_nutricionales_aux,
                }

                if texto_buscar == "":
                    menus[menu.receta.categoria.nombre].append(plato)
                else:
                    menus_buscar.append(plato)
            if texto_buscar == "":
                return Response({"success": menus}, status=status.HTTP_200_OK)
            else:
                return Response({"success": menus_buscar}, status=status.HTTP_200_OK)

        return Response({"error": "Algo ha ido mal, comprueba los datos introducidos"},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def crea_pedido(request):
    try:
        """
        raciones = models.IntegerField(default=1)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    direccion = models.ForeignKey(DireccionCliente, on_delete=models.CASCADE)
    menu = models.ForeignKey(ComponenteMenu, on_delete=models.CASCADE)
    facturado = models.BooleanField(default=False)
        """
        cantidad = request.POST['cantidad']
        id_direccion = request.POST['id_direccion']
        id_componente_menu = request.POST['id_componente_menu']

        user = request.user
        cliente = Cliente.objects.get(user=user)

        if cantidad and id_direccion and id_componente_menu and cantidad:  # debemos actualizar
            if id_direccion == '0':
                empresa = Empresa.objects.get(id_empresa=cliente.id_empresa.id_empresa)
                direccion_empresa = DireccionEmpresa.objects.get(cliente=empresa)
                direccion_cliente = None
            else:
                direccion_cliente = DireccionCliente.objects.get(id=id_direccion, cliente=cliente)
                direccion_empresa = None
            componente_menu = ComponenteMenu.objects.get(id=id_componente_menu)

            try:
                pedido = LineaPedido.objects.get(cliente=cliente, direccion_cliente=direccion_cliente,
                                                 direccion_empresa=direccion_empresa, menu=componente_menu)
                if pedido.raciones > 0:
                    pedido.raciones = pedido.raciones + int(cantidad)
                    pedido.save()
            except LineaPedido.DoesNotExist as e:
                pedido = LineaPedido(cliente=cliente, direccion_cliente=direccion_cliente,
                                     direccion_empresa=direccion_empresa, menu=componente_menu,
                                     raciones=cantidad)
                pedido.save()

            return Response({"success": "Pedido guardado correctamente"}, status=status.HTTP_200_OK)

        return Response({"error": "Algo ha ido mal, comprueba los datos introducidos"},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def get_pedidos(request):
    try:
        fecha = request.POST['fecha']

        user = request.user
        cliente = Cliente.objects.get(user=user)

        if fecha:  # debemos actualizar
            date_time_obj = datetime.datetime.strptime(fecha, '%Y-%m-%d')
            fecha_max = date_time_obj + datetime.timedelta(days=30)
            fecha_min = date_time_obj + datetime.timedelta(days=-30)

            pedidos = LineaPedido.objects.filter(cliente=cliente, menu__menu__dia__gt=fecha_min,
                                                 menu__menu__dia__lt=fecha_max)
            lista_pedidos = {}
            for pedido in pedidos:
                fecha = "" + str(pedido.menu.menu.dia.year) + "-" + str(
                    '{:02d}'.format(pedido.menu.menu.dia.month)) + "-" + str('{:02d}'.format(pedido.menu.menu.dia.day))

                if pedido.direccion_cliente:
                    direccion = pedido.direccion_cliente.direccion
                elif pedido.direccion_empresa:  # direccion_empresa
                    direccion = pedido.direccion_empresa.direccion
                else:
                    direccion = ""

                if fecha not in lista_pedidos:
                    lista_pedidos[fecha] = []

                pedido_detalle = {
                    "id_linea_pedido": pedido.id,
                    "raciones": pedido.raciones,
                    "nombre_plato": pedido.menu.receta.nombre,
                    "facturado": pedido.facturado,
                    "precio": pedido.menu.precio,
                    "direccion": direccion
                }

                lista_pedidos[fecha].append(pedido_detalle)

            date_generated = [fecha_min + datetime.timedelta(days=x) for x in range(0, (fecha_max - fecha_min).days)]

            for date in date_generated:
                if date.strftime("%Y-%m-%d") not in lista_pedidos:
                    lista_pedidos[date.strftime("%Y-%m-%d")] = []
                print(date.strftime("%d-%m-%Y"))

            return Response({"success": lista_pedidos}, status=status.HTTP_200_OK)

        return Response({"error": "Algo ha ido mal, comprueba los datos introducidos"},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def borra_pedido(request):
    try:
        user = request.user
        cliente = Cliente.objects.get(user=user)

        id_pedido = request.POST['id_pedido']

        if id_pedido:  # debemos actualizar
            pedido = LineaPedido.objects.get(cliente=cliente, id=id_pedido)
            pedido.delete()

            return Response({"success": "Pedido eliminado correctamente"}, status=status.HTTP_200_OK)

        return Response({"error": "Algo ha ido mal, comprueba los datos introducidos"},
                        status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def busqueda_menus():
    return True


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def modifica_pedido():
    return True


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, EsUsuario])
def get_pedidos_completos():
    return True
