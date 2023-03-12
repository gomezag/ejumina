
from django.contrib.auth import authenticate
from rest_framework import serializers
from eventos.models import Usuario

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario.objects.create_user(validated_data['username'],
                                        None,
                                        validated_data['password'])
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'username')


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")


class EventoSerializer(serializers.Serializer):
    nombre = serializers.CharField(source='name')
    _id = serializers.CharField(source='pk')


class PersonaSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    apellido = serializers.CharField(source='nombre')
    CI = serializers.CharField(source='cedula')

