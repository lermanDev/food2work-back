from django.core.management.base import BaseCommand
from ingredientes.models import Ingrediente, DatoNutricional, InfoNutricional


class Command(BaseCommand):

    def handle(self, *args, **options):
        import requests
        import string
        import xmltodict

        HEADER = {
            'Content-Type': 'application/xml',
            "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0'}

        url_consultas = 'https://www.bedca.net/bdpub/procquery.php'
        proxies = ''

        d = dict.fromkeys(string.ascii_lowercase, 0)

        query_alfabeto = '<?xml version="1.0" encoding="utf-8"?><foodquery><type level="1"/><selection><atribute ' \
                         'name="f_id"/><atribute name="f_ori_name"/><atribute name="langual"/><atribute ' \
                         'name="f_eng_name"/><atribute name="f_origen"/><atribute ' \
                         'name="edible_portion"/></selection><condition><cond1><atribute1 ' \
                         'name="f_ori_name"/></cond1><relation ' \
                         'type="BEGINW"/><cond3></cond3></condition><condition><cond1><atribute1 ' \
                         'name="f_origen"/></cond1><relation type="EQUAL"/><cond3>BEDCA</cond3></condition><order ' \
                         'ordtype="ASC"><atribute3 name="f_ori_name"/></order></foodquery> '

        query_producto = '<?xml version="1.0" encoding="utf-8"?><foodquery><type level="2"/><selection><atribute ' \
                         'name="f_id"/><atribute name="f_ori_name"/><atribute name="f_eng_name"/><atribute ' \
                         'name="sci_name"/><atribute name="langual"/><atribute name="foodexcode"/><atribute ' \
                         'name="mainlevelcode"/><atribute name="codlevel1"/><atribute name="namelevel1"/><atribute ' \
                         'name="codsublevel"/><atribute name="codlevel2"/><atribute name="namelevel2"/><atribute ' \
                         'name="f_des_esp"/><atribute name="f_des_ing"/><atribute name="photo"/><atribute ' \
                         'name="edible_portion"/><atribute name="f_origen"/><atribute name="c_id"/><atribute ' \
                         'name="c_ori_name"/><atribute name="c_eng_name"/><atribute name="eur_name"/><atribute ' \
                         'name="componentgroup_id"/><atribute name="glos_esp"/><atribute name="glos_ing"/><atribute ' \
                         'name="cg_descripcion"/><atribute name="cg_description"/><atribute ' \
                         'name="best_location"/><atribute name="v_unit"/><atribute name="moex"/><atribute ' \
                         'name="stdv"/><atribute name="min"/><atribute name="max"/><atribute name="v_n"/><atribute ' \
                         'name="u_id"/><atribute name="u_descripcion"/><atribute name="u_description"/><atribute ' \
                         'name="value_type"/><atribute name="vt_descripcion"/><atribute name="vt_description"/><atribute ' \
                         'name="mu_id"/><atribute name="mu_descripcion"/><atribute name="mu_description"/><atribute ' \
                         'name="ref_id"/><atribute name="citation"/><atribute name="at_descripcion"/><atribute ' \
                         'name="at_description"/><atribute name="pt_descripcion"/><atribute ' \
                         'name="pt_description"/><atribute name="method_id"/><atribute name="mt_descripcion"/><atribute ' \
                         'name="mt_description"/><atribute name="m_descripcion"/><atribute ' \
                         'name="m_description"/><atribute name="m_nom_esp"/><atribute name="m_nom_ing"/><atribute ' \
                         'name="mhd_descripcion"/><atribute ' \
                         'name="mhd_description"/></selection><condition><cond1><atribute1 name="f_id"/></cond1><relation ' \
                         'type="EQUAL"/><cond3>{}</cond3></condition><condition><cond1><atribute1 ' \
                         'name="publico"/></cond1><relation type="EQUAL"/><cond3>1</cond3></condition><order ' \
                         'ordtype="ASC"><atribute3 name="componentgroup_id"/></order></foodquery> '

        # CREAMOS UNA SESION Y SOLICITAMOS LA PÁGINA DEL PRODUCTO
        sesion = requests.session()
        sesion.headers.update(HEADER)
        sesion.proxies.update(proxies)

        # AHORA SOLICITAMOS EL PRODUCTO
        pagina_devuelta = sesion.post(url_consultas, headers=HEADER, data=query_alfabeto, proxies=proxies)

        listado_productos = xmltodict.parse(pagina_devuelta.content)

        for producto_l in listado_productos['foodresponse']['food']:
            pagina_producto = sesion.post(url_consultas, headers=HEADER, data=query_producto.format(producto_l['f_id']),
                                          proxies=proxies)
            producto = xmltodict.parse(pagina_producto.content)['foodresponse']['food']
            if producto:
                nombre_ingrediente = producto['f_ori_name']
                unidad_ingrediente = 'g'
                equivalencia_gramos_ingrediente = 1
                try:
                    ingrediente = Ingrediente.objects.get(nombre=nombre_ingrediente)
                except Ingrediente.DoesNotExist:
                    ingrediente = Ingrediente(nombre=nombre_ingrediente, unidad=unidad_ingrediente,
                                              equivalencia_en_gramos=equivalencia_gramos_ingrediente)
                    ingrediente.save()
                try:
                    for dato_nutricional in producto['foodvalue']:
                        nombre_dato_nutricional = dato_nutricional['c_ori_name']
                        unidad_dato_nutricional = dato_nutricional['v_unit']
                        tipo_dato_nutricional = dato_nutricional['cg_descripcion']

                        try:
                            datonutricional = DatoNutricional.objects.get(nombre=nombre_dato_nutricional)
                        except DatoNutricional.DoesNotExist:
                            datonutricional = DatoNutricional(nombre=nombre_dato_nutricional, tipo=tipo_dato_nutricional,
                                                              unidad=unidad_dato_nutricional)
                            datonutricional.save()

                        valor_dato_nutricional_en_ingrediente = dato_nutricional['best_location']

                        if valor_dato_nutricional_en_ingrediente:
                            try:
                                infonutricional = InfoNutricional.objects.get(ingrediente=ingrediente,
                                                                              dato_nutricional=datonutricional)
                                if infonutricional.valor != float(valor_dato_nutricional_en_ingrediente):
                                    raise Exception("Ha habido un error en: " + nombre_ingrediente + " " + nombre_dato_nutricional + " " + str(infonutricional.valor) + " " + str(valor_dato_nutricional_en_ingrediente))
                            except InfoNutricional.DoesNotExist:
                                infonutricional = InfoNutricional(ingrediente=ingrediente,
                                                                  dato_nutricional=datonutricional,
                                                                  valor=valor_dato_nutricional_en_ingrediente,
                                                                  cantidad=100)
                                infonutricional.save()
                                print("Creado: " + nombre_ingrediente + " " + nombre_dato_nutricional)
                except Exception as e:
                    print("ERROR CREANDO INGREDIENTE " + nombre_ingrediente)
                    ingrediente.delete()
            else:
                print("INGREDIENTE INCORRECTO: " + str(producto_l))

