from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from serviceScheduleBack.access.views import (UserViewSet, UserRegister,
                                              PerfilViewSet, PerfilUpdate)

from serviceScheduleBack.schedule.views import ScheduleViewSet, EventViewSet


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'perfil', PerfilViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'events', EventViewSet, 'events')

urlpatterns = [
    path('api/', include(router.urls)),

    path('api/perfil/update', PerfilUpdate.as_view(), name='perfil_update'),
    path('api/users/register', UserRegister.as_view(), name='user_register'),
    
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify', TokenVerifyView.as_view(), name='token_verify'),

    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('admin/', admin.site.urls),
]
