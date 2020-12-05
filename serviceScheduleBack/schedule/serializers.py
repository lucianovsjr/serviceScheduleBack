from rest_framework import serializers

from .models import Schedule, Event, Appointment


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = [
            'id',
            'date_start',
            'date_end',
            'hours_start',
            'hours_end',
            'time_range'
        ]


class EventSerializer(serializers.ModelSerializer):
    week_days = serializers.ListField(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    hours_start = serializers.TimeField(source='get_hours_start', read_only=True)
    hours_end = serializers.TimeField(source='get_hours_end', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'


class ProviderMonthSerializer(serializers.Serializer):
    date = serializers.CharField(max_length=6)
    vacancies_total = serializers.IntegerField(default=0)
    vacancies_morning = serializers.IntegerField(default=0)
    vacancies_afternoon = serializers.IntegerField(default=0)
    vacancies_night = serializers.IntegerField(default=0)


class AppointmentMonthSerializer(serializers.Serializer):
    id = serializers.IntegerField(default=0)
    date = serializers.DateField(read_only=True)
    time = serializers.TimeField(read_only=True)
    canceled_at = serializers.DateTimeField(read_only=True)
    user_id = serializers.IntegerField(default=0)
    loose_client = serializers.CharField(max_length=30)
    status = serializers.CharField(max_length=10)


class MyAppointmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(default=0)
    date_time = serializers.DateTimeField(read_only=True)
    canceled_at = serializers.DateTimeField(read_only=True)
    provider_id = serializers.IntegerField(default=0)
    provider_name = serializers.CharField(max_length=30)
    image_name = serializers.CharField(max_length=50)


class NotificationAppointmentSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)
