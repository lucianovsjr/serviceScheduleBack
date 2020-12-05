from django.utils import timezone
from django.http import Http404, HttpResponse, JsonResponse

from rest_framework import status, permissions, viewsets, generics
from rest_framework.response import Response

from .models import Schedule, Event, Appointment
from serviceScheduleBack.schedule import serializers


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = serializers.ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Schedule.objects.filter(
            provider=self.request.user).order_by('-date_start', '-hours_start')

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
            return Response(
                {'msg': 'Período já possui agendamentos'},
                status=status.HTTP_202_ACCEPTED,
                headers=headers
            )

        schedule.save()
        schedule.create_appointments()
        return Response(
            serializer.validated_data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        if serializer.is_valid(raise_exception=True):
            headers = self.get_success_headers(serializer.validated_data)
            check_start = instance.check_update_start(
                            serializer.validated_data['date_start'],
                            serializer.validated_data['hours_start']
                        )
            check_end = instance.check_update_end(
                            serializer.validated_data['date_end'],
                            serializer.validated_data['hours_end']
                        )

            if not check_start['check'] or not check_end['check']:
                return Response(
                    {'msg': 'Horário com conflito ou existe cliente(s) agendado(s).'},
                    status=status.HTTP_202_ACCEPTED,
                    headers=headers
                )

            if check_start['appointments_delete']:
                check_start['appointments_delete'].delete()
            if check_start['appointments_delete_fix_day']:
                check_start['appointments_delete_fix_day'].delete()
            if check_end['appointments_delete']:
                check_end['appointments_delete'].delete()
            if check_end['appointments_delete_fix_day']:
                check_end['appointments_delete_fix_day'].delete()

            for appointment_create in (
                check_start['appointments_create'],
                check_end['appointments_create']
             ):
                if None not in appointment_create.values():
                    instance.base_create_appointments(
                        appointment_create['date_start'],
                        appointment_create['date_end'],
                        appointment_create['hours_start'],
                        appointment_create['hours_end']
                    )
                if None not in appointment_create['fix_day'].values():
                    instance.base_create_appointments(
                        appointment_create['fix_day']['date_start'],
                        appointment_create['fix_day']['date_end'],
                        appointment_create['fix_day']['hours_start'],
                        appointment_create['fix_day']['hours_end']
                    )

            serializer.save()

            return Response(
                serializer.validated_data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

    def destroy(self, request, pk):
        instance = self.get_object()
        if not instance.check_delete():
            return Response(
                {'msg': 'Agenda com cliente(s) agendado(s)'},
                status=status.HTTP_202_ACCEPTED
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EventSerializer
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
        serializer = serializers.EventSerializer(events, many=True)

        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)

        event = Event(**serializer.validated_data)
        if event.appointments_exists():
            return Response(
                {'msg': 'Período já possui evento'},
                status=status.HTTP_202_ACCEPTED,
                headers=headers
            )
        event.save()

        event.update_appointments()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

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


class ProviderMonthViewSet(generics.RetrieveAPIView):
    serializer_class = serializers.ProviderMonthSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, pk):
        provider_months = []
        appointments = Appointment.objects.filter(
            provider=pk,
            event=None,
            date_time__date__gte=timezone.localtime(timezone.now()).date()
        ).order_by('date_time')

        for appointment in appointments:
            date_time = str(appointment.date_time.year) + str(
                appointment.date_time.month)

            exists = False
            for provider_month in provider_months:
                if date_time == provider_month['date']:
                    exists = True

            if not exists:
                provider_months.append({
                    'date': date_time,
                    'vacancies_total': 0,
                    'vacancies_morning': 0,
                    'vacancies_afternoon': 0,
                    'vacancies_night': 0
                })

            for provider_month in provider_months:
                if date_time == provider_month['date']:
                    provider_month['vacancies_total'] += 1
                    date_tz = timezone.localtime(appointment.date_time)

                    if date_tz.hour >= 18:
                        provider_month['vacancies_night'] += 1
                    elif date_tz.hour >= 12:
                        provider_month['vacancies_afternoon'] += 1
                    elif date_tz.hour >= 6:
                        provider_month['vacancies_morning'] += 1
                    else:
                        # appointment.date_time.hour < 6
                        provider_month['vacancies_night'] += 1

                    break

        serializer = serializers.ProviderMonthSerializer(
            provider_months,
            many=True
        )
        return Response(serializer.data)


class AppointmentMonthViewSet(generics.ListAPIView):
    serializer_class = serializers.AppointmentMonthSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        year = request.query_params['year']
        month = request.query_params['month']
        provider_id = request.query_params['providerId']

        appointments = Appointment.objects.filter(
            date_time__year=year,
            date_time__month=month,
            date_time__date__gte=timezone.localtime(timezone.now()).date(),
            provider=provider_id, event=None
        ).order_by('date_time')

        appointments_month = []
        for appointment in appointments:
            date_tz = timezone.localtime(appointment.date_time)
            appointments_month.append({
                'id': appointment.id,
                'date': date_tz.date(),
                'time': date_tz.time(),
                'canceled_at': timezone.localtime(appointment.canceled_at),
                'user_id': appointment.user.id if appointment.user else None,
                'loose_client': appointment.loose_client,
                'status': appointment.get_status(self.request.user)
            })

        serializer = serializers.AppointmentMonthSerializer(
            appointments_month,
            many=True
        )
        return Response(serializer.data)


class AppointmentUpdateStatusViewSet(generics.UpdateAPIView):
    serializer_class = serializers.AppointmentMonthSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, pk=None):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return HttpResponse(status=404)

        if (appointment.user and not appointment.canceled_at):
            # Cancelar
            if (appointment.user == self.request.user
                    or appointment.provider == self.request.user):
                appointment.loose_client = ''
                appointment.canceled_at = timezone.now()
                appointment.status = Appointment.FREE
        else:
            appointment.user = self.request.user
            appointment.loose_client = self.request.user.get_full_name()
            appointment.canceled_at = None
            appointment.status = Appointment.SCHEDULED
        appointment.save()

        serializer = serializers.AppointmentMonthSerializer(appointment)
        return JsonResponse(serializer.data)


class MyAppointmentViewSet(generics.ListAPIView):
    serializer_class = serializers.MyAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        appointments = Appointment.objects.filter(
            user=self.request.user,
            canceled_at=None,
            date_time__date__gte=timezone.localtime(timezone.now()).date()
        ).order_by('date_time')

        appointments_ = []
        for appointment in appointments:
            appointments_.append({
                'id': appointment.id,
                'date_time': timezone.localtime(appointment.date_time),
                'canceled_at': appointment.canceled_at,
                'provider_id': appointment.provider.id,
                'provider_name': appointment.provider.get_full_name(),
                'image_name': (appointment.provider.user_perfil.image_name()
                               if appointment.provider.user_perfil.image
                               else '')
            })

        serializer = serializers.MyAppointmentSerializer(
            appointments_,
            many=True
        )

        return JsonResponse(serializer.data, safe=False)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = serializers.AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = serializers.AppointmentSerializer(data=self.request.data)

        if serializer.is_valid(raise_exception=True):
            appointment = Appointment(**serializer.validated_data)
            appointment.company = appointment.provider.user_perfil.company
            appointment.user = self.request.user
            appointment.status = Appointment.SCHEDULED
            if appointment.appointment_exist():
                return JsonResponse(
                    {'msg': 'Período já possui agendamento'},
                    status=400
                )
            appointment.save()
            return JsonResponse(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return JsonResponse(status=400)

    def update(self, request, pk=None):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return HttpResponse(status=404)

        serializer = serializers.AppointmentSerializer(
            appointment,
            data=self.request.data
        )

        if serializer.is_valid():
            appointment.loose_client = serializer.validated_data[
                'loose_client']
            appointment.user = self.request.user
            appointment.canceled_at = None
            appointment.status = Appointment.SCHEDULED
            if not appointment.schedule:
                appointment.date_time = serializer.validated_data['date_time']
                appointment.time_range = serializer.validated_data[
                    'time_range']
            if appointment.appointment_exist():
                return JsonResponse(
                    {'msg': 'Horário já possui agendamento'},
                    status=400
                )
            appointment.save()
            return JsonResponse(serializer.data)

        return JsonResponse(status=400)


class NotificationBusyListView(generics.ListAPIView):
    serializer_class = serializers.NotificationAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        appointments = Appointment.objects.filter(
            provider=self.request.user,
            send_notification=True
        ).order_by('date_time')

        messages = []
        for appointment in appointments:
            if appointment.status == Appointment.BUSY:
                messages.append({
                    'message': ' '.join([
                        'Horário',
                        timezone.localtime(appointment.date_time).strftime(
                            '%d/%m/%Y %H:%M'),
                        'foi reservado para a agenda do(a)',
                        appointment.provider_busy.get_full_name()
                    ])
                })
            elif appointment.status == Appointment.FREE:
                messages.append({
                    'message': ' '.join([
                        'Horário',
                        timezone.localtime(appointment.date_time).strftime(
                            '%d/%m/%Y %H:%M'),
                        'foi liberado da agenda do(a)',
                        appointment.provider_busy.get_full_name()
                    ])
                })
                appointment.provider_busy = None
            appointment.send_notification = False
            appointment.save()

        serializer = serializers.NotificationAppointmentSerializer(
            messages,
            many=True
        )

        return JsonResponse(serializer.data, safe=False)
