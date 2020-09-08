from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .access.views import UserViewSet, UserRegister, PerfilViewSet


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'perfil', PerfilViewSet)

urlpatterns = [
    path('api/', include(router.urls)),

    path('api/users/register', UserRegister.as_view(), name='user_register'),
    
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify', TokenVerifyView.as_view(), name='token_verify'),

    path('admin/', admin.site.urls),
]
