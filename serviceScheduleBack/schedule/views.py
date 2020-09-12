from django.shortcuts import render

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Schedule
from .serializers import ScheduleSerializer
from .mixin import check_period


class ScheduleViewset(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Schedule.objects.filter(provider=self.request.user)

    def create(self, request):        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        
        if not check_period(
            serializer.validated_data['date_start'],
            serializer.validated_data['date_end'],
            serializer.validated_data['hours_start'],
            serializer.validated_data['hours_end']
            ):
            return Response({'msg': 'Período já possui agendamentos'},
                status=status.HTTP_202_ACCEPTED, headers=headers)

        schedule = Schedule(
            provider=self.request.user,
            date_start=serializer.validated_data['date_start'],
            date_end=serializer.validated_data['date_end'],
            hours_start=serializer.validated_data['hours_start'],
            hours_end=serializer.validated_data['hours_end'],
            time_range=serializer.validated_data['time_range'],
        )
        schedule.save()
        schedule.create_appointments()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED, headers=headers)
