from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Perfil


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User(**validated_data)
        # user.username = validated_data['email']
        user.set_password(password)
        user.save()

        perfil = Perfil(user=user)
        perfil.save()

        return user


class PerfilSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id')
    name = serializers.CharField(source='user.get_full_name')
    email = serializers.CharField(source='user.email')
    image_name = serializers.CharField(source='image.name')

    class Meta:
        model = Perfil
        fields = [
            'id',
            'name',
            'email',
            'provider',
            'fantasy_name',
            'profession',
            'image_name'
        ]


class PerfilUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(source='user.get_full_name')
