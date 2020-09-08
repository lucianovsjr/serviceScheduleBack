from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, generics

from .serializers import UserSerializer, RegisterSerializer, PerfilSerializer
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
        return Perfil.objects.filter(id=self.request.user.id)
