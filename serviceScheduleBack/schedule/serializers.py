from rest_framework import serializers

from .models import Schedule, Event


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'date_start', 'date_end', 'hours_start',
                    'hours_end', 'time_range']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
