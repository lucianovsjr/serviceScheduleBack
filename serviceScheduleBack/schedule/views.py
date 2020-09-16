from django.shortcuts import render
from django.http import Http404

from rest_framework import status, permissions, viewsets
from rest_framework.response import Response

from .models import Schedule, Event
from .serializers import ScheduleSerializer, EventSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Schedule.objects.filter(provider=self.request.user)

    def create(self, request):        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)

        schedule = Schedule(
            provider=self.request.user,
            date_start=serializer.validated_data['date_start'],
            date_end=serializer.validated_data['date_end'],
            hours_start=serializer.validated_data['hours_start'],
            hours_end=serializer.validated_data['hours_end'],
            time_range=serializer.validated_data['time_range'],
        )

        if schedule.appointments_exists():
            return Response({'msg': 'Período já possui agendamentos'},
                status=status.HTTP_202_ACCEPTED, headers=headers)

        schedule.save()
        schedule.create_appointments()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED, headers=headers)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(schedule__provider=self.request.user)

    def retrieve(self, request, pk):
        queryset = self.get_queryset()
        try:            
            schedule = Schedule.objects.get(pk=pk)
        except Schedule.DoesNotExist:
            raise Http404("Não existe agendamento.")

        events = queryset.filter(schedule=schedule)        
        serializer = EventSerializer(events, many=True)

        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)            

        event = Event(**serializer.validated_data)
        if event.appointments_exists():
            return Response({'msg': 'Período já possui evento'},
                status=status.HTTP_202_ACCEPTED, headers=headers)
        event.save()

        event.update_appointments()

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)        
        serializer.save()

        instance.clear_appointment()
        instance.update_appointments()

        return Response(serializer.data)

    def destroy(self, request, pk):
        instance = self.get_object()
        instance.clear_appointment()           
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
