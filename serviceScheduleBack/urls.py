from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from serviceScheduleBack.access.views import (
    UserViewSet,
    UserRegister,
    PerfilViewSet,
    PerfilUpdate,
    ProviderViewSet
)

from serviceScheduleBack.schedule.views import (
    ScheduleViewSet, EventViewSet, ProviderMonthViewSet,
    AppointmentMonthViewSet, AppointmentUpdateStatusViewSet,
    MyAppointmentViewSet, AppointmentViewSet
)


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'perfil', PerfilViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'events', EventViewSet, 'events')
router.register(r'appointment', AppointmentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),

    path('api/perfil/update', PerfilUpdate.as_view(), name='perfil_update'),

    path('api/providers/', ProviderViewSet.as_view(), name='provider_list'),
    path('api/providers/months/<int:pk>/', ProviderMonthViewSet.as_view(),
         name='provider_months'),

    path('api/users/register', UserRegister.as_view(), name='user_register'),

    path('api/appointments/months/', AppointmentMonthViewSet.as_view(),
         name='appointments_months'),
    path('api/appointments/status/<int:pk>/',
         AppointmentUpdateStatusViewSet.as_view(),
         name='appointments_update_status'),

    path('api/myappointments/', MyAppointmentViewSet.as_view(),
         name='my_appointments'),

    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('api/token/verify', TokenVerifyView.as_view(), name='token_verify'),

    path('api/auth/', include('rest_framework.urls',
         namespace='rest_framework')),

    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
