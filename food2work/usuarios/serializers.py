from django.contrib.auth.models import User, Group
from rest_framework import serializers
from usuarios.models import Cliente, DireccionCliente, Empresa, DireccionEmpresa, User


class ClienteSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    username = serializers.EmailField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField()

    def create(self, validate_data):
        instance_user = User()
        instance_cliente = Cliente()

        instance_user.first_name = validate_data.get('first_name')
        instance_user.last_name = validate_data.get('last_name')
        instance_user.username = validate_data.get('username')
        instance_user.email = validate_data.get('email')
        instance_user.set_password(validate_data.get('password'))

        instance_user.save()

        instance_cliente.user = instance_user
        instance_cliente.save()

        return instance_cliente.user

    def validate_username(self, data):
        users = Cliente.objects.filter(user__username=data)  # User.objects.filter(username=data)

        if len(users) != 0:
            raise serializers.ValidationError("Ya existe un usuario con este correo, ingrese uno nuevo")
        else:
            return data

