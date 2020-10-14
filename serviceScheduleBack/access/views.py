from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    PerfilSerializer,
    PerfilUpdateSerializer
)
from .models import Perfil


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Perfil.objects.filter(user=self.request.user)

class PerfilUpdate(generics.UpdateAPIView):
    queryset = Perfil.objects.all()
    serializer_class = PerfilUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.request.user
        user.first_name = request.data['name']
        user.save()

        perfil = self.request.user.user_perfil
        perfil.fantasy_name = request.data['fantasy_name']
        perfil.profession = request.data['profession']
        perfil.save()

        content = {
            'name': user.first_name,
            'fantasy_name': perfil.fantasy_name,
            'profession': perfil.profession
        }

        return Response(content, status=status.HTTP_200_OK)


class ProviderViewSet(generics.ListAPIView):
    queryset = Perfil.objects.filter(provider=True)
    serializer_class = PerfilSerializer
    permission_classes = [permissions.IsAuthenticated]
