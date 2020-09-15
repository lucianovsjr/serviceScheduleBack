from datetime import datetime, timedelta
from django.db import models


class Schedule(models.Model):
    provider = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date_start = models.DateField('Data inicial')
    date_end = models.DateField('Data final')
    hours_start = models.TimeField('Hora inicial')
    hours_end = models.TimeField('Hora Final')
    time_range = models.IntegerField('Tempo de atendimento', default=0)

    def __str__(self):
        return '{} {} - {} {} - {}'.format(self.date_start, self.hours_start,
                                        self.date_end, self.hours_end,
                                        self.time_range)

    def create_appointments(self):
        date_time = datetime(self.date_start.year, self.date_start.month,
                            self.date_start.day, self.hours_start.hour,
                            self.hours_start.minute)
        date_time_end = datetime(self.date_end.year, self.date_end.month,
                                self.date_end.day, self.hours_end.hour,
                                self.hours_end.minute)
        minutes = timedelta(minutes=self.time_range)
        day = timedelta(days=1)
        hour_start = self.hours_start.hour
        minute_start = self.hours_start.minute
        hour_end = self.hours_end.hour
        minute_end = self.hours_end.minute

        while (date_time <= date_time_end):
            appointment = Appointment(
                schedule=self,
                provider=self.provider,
                date_time=date_time
            )
            appointment.save()

            if (date_time.time() >= self.hours_start
                and date_time.time() < self.hours_end):
                date_time += minutes
            else:
                date_time += day
                date_time = date_time.replace(hour=hour_start,
                                minute=minute_start)

    def appointments_exists(self):
        appointments = Appointment.objects.filter(
            date_time__date__range=(self.date_start, self.date_end),
            date_time__time__range=(self.hours_start, self.hours_end)
        )
    
        return appointments.count() > 0


class Event(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField('Nome', max_length=30)
    week = models.CharField('Semana', max_length=7)
    date = models.DateField('Data')
    hours_start = models.TimeField('Hora inicial')
    hours_end = models.TimeField('Hora Final')
    all_day = models.BooleanField('Todo dia', default=False)

    def week_days(self):
        ret_week = []
        for day in enumerate(self.week):
            if day[1] == '1':
                ret_week.append(day[0] + 1)
        
        return ret_week

    def clear_appointment(self):
        for appointment in self.appointment_event.all():
            appointment.event = None
            appointment.save()

    def update_appointments(self):        
        appointments = self.schedule.appointment_schedule.all()        
        if self.date:
            appointments = appointments.filter(date_time__date=self.date)
        else:
            appointments = appointments.filter(
                    date_time__week_day__in=self.week_days())
        if not self.all_day:
            appointments = appointments.filter(
                    date_time__time__range=(self.hours_start, self.hours_end))

        for appointment in appointments:
            appointment.event = self
            appointment.save()

    def appointments_exists(self):
        appointments = Appointment.objects.exclude(event=None)
        if self.date:
            appointments = appointments.filter(date_time__date=self.date)
        else:
            appointments = appointments.filter(
                    date_time__week_day__in=self.week_days)
        if not self.all_day:
            appointments = appointments.filter(
                    date_time__time__range=(self.hours_start, self.hours_end))

        return appointments.count() > 0


class Appointment(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE,
                                related_name='appointment_schedule')
    provider = models.ForeignKey('auth.User', verbose_name='Provider',
                                on_delete=models.CASCADE,
                                related_name='appointment_provider')
    user = models.ForeignKey('auth.User', verbose_name='Usuário',
                                on_delete=models.CASCADE,
                                related_name='appointment_user',
                                null=True, blank=True)
    date_time = models.DateTimeField('Data')
    canceled_at = models.DateTimeField(null=True, blank=True)
    loose_client = models.CharField('Cliente avulso', max_length=30,
                                    blank=True)
    time_range = models.IntegerField('Tempo de atendimento', default=0)
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING,
                            related_name='appointment_event',
                            null=True)

    def __str__(self):
        return '{}'.format(self.date_time)

    def available(self):
        return not self.user
