from datetime import datetime, timedelta, time

from django.db import models
from django.utils import timezone

from serviceScheduleBack.access.models import Company


class Schedule(models.Model):
    provider = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date_start = models.DateField('Data inicial')
    date_end = models.DateField('Data final')
    hours_start = models.TimeField('Hora inicial')
    hours_end = models.TimeField('Hora Final')
    time_range = models.IntegerField('Tempo de atendimento', default=0)

    def __str__(self):
        return '{}  {} {} - {} {}'.format(self.provider, self.date_start,
                                          self.hours_start, self.date_end,
                                          self.hours_end)

    def create_appointments(self):
        tzinfo = timezone.localtime().tzinfo
        date_time = datetime(
            self.date_start.year,
            self.date_start.month,
            self.date_start.day,
            self.hours_start.hour,
            self.hours_start.minute,
            tzinfo=tzinfo
        )
        date_time_end = datetime(
            self.date_end.year,
            self.date_end.month,
            self.date_end.day,
            self.hours_end.hour,
            self.hours_end.minute,
            tzinfo=tzinfo
        )

        minutes = timedelta(minutes=self.time_range)
        day = timedelta(days=1)
        hour_start = self.hours_start.hour
        minute_start = self.hours_start.minute

        while (date_time < date_time_end):
            appointment = Appointment(
                schedule=self,
                provider=self.provider,
                company=self.provider.user_perfil.company,
                date_time=date_time,
                time_range=self.time_range
            )
            appointment.save()

            date_time += minutes
            if not (date_time.time() >= self.hours_start
                    and date_time.time() < self.hours_end):
                date_time += day
                date_time = date_time.replace(
                    hour=hour_start,
                    minute=minute_start
                )

    def appointments_exists(self):
        appointments = Appointment.objects.filter(
            provider=self.provider,
            date_time__date__range=(self.date_start, self.date_end),
            date_time__time__range=(self.hours_start, self.hours_end)
        )

        return appointments.count() > 0


class Event(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField('Nome', max_length=30)
    week = models.CharField('Semana', max_length=7)
    date = models.DateField('Data', null=True)
    hours_start = models.TimeField('Hora inicial')
    hours_end = models.TimeField('Hora Final')
    all_day = models.BooleanField('Todo dia', default=False)

    def week_days(self):
        ret_week = []
        for day in enumerate(self.week):
            ret_week.append(day[1] == '1')

        return ret_week

    def _week_days(self):
        ret_week = []
        for day in enumerate(self.week):
            if day[1] == '1':
                ret_week.append(day[0] + 1)

        return ret_week

    def clear_appointment(self):
        for appointment in self.appointment_event.all():
            appointment.event = None
            appointment.status = Appointment.FREE
            appointment.save()

    def update_appointments(self):
        appointments = self.schedule.appointment_schedule.all()
        if self.date:
            appointments = appointments.filter(date_time__date=self.date)
        else:
            appointments = appointments.filter(
                    date_time__week_day__in=self._week_days())
        if not self.all_day:
            hours_end = (datetime.combine(datetime.now().date(),
                                          self.hours_end)
                         - timedelta(minutes=1)).time()
            appointments = appointments.filter(
                    date_time__time__range=(self.hours_start, hours_end))

        for appointment in appointments:
            appointment.event = self
            appointment.status = Appointment.BUSY
            appointment.save()

    def appointments_exists(self):
        # Verifica se já existe evento para o período
        appointments = Appointment.objects.filter(
            schedule__provider=self.schedule.provider).exclude(event=None)
        if self.date:
            appointments = appointments.filter(date_time__date=self.date)
        else:
            appointments = appointments.filter(
                    date_time__week_day__in=self._week_days())
        if not self.all_day:
            hours_end = (datetime.combine(datetime.now().date(),
                                          self.hours_end)
                         - timedelta(minutes=1)).time()
            appointments = appointments.filter(
                    date_time__time__range=(self.hours_start, hours_end))

        return appointments.count() > 0


class Appointment(models.Model):
    FREE = '0'
    SCHEDULED = '1'
    BUSY = '2'
    STATUS_CHOICES = [
        (FREE, 'Livre'),
        (SCHEDULED, 'Agendado'),
        (BUSY, 'Ocupado')
    ]

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE,
                                 related_name='appointment_schedule',
                                 blank=True, null=True)
    provider = models.ForeignKey('auth.User', verbose_name='Provider',
                                 on_delete=models.CASCADE,
                                 related_name='appointment_provider')
    user = models.ForeignKey('auth.User', verbose_name='Usuário',
                             on_delete=models.CASCADE,
                             related_name='appointment_user',
                             null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    date_time = models.DateTimeField('Data')
    canceled_at = models.DateTimeField(null=True, blank=True)
    loose_client = models.CharField('Cliente avulso', max_length=30,
                                    blank=True)
    time_range = models.IntegerField('Tempo de atendimento', default=0)
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING,
                              related_name='appointment_event',
                              blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              default=FREE, blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(
            self.provider,
            timezone.localtime(self.date_time))

    def available(self):
        return not self.user

    def get_status(self, user):
        # Status para o mobile
        # cancel, busy, schedule
        IS_OWNER = self.provider == user or self.user == user

        if self.status in (self.SCHEDULED, self.BUSY) and not IS_OWNER:
            return 'busy'

        if IS_OWNER and self.status == self.SCHEDULED:
            return 'cancel'

        if self.status == self.FREE:
            return 'schedule'

        return 'busy'

    def get_hours_start(self):
        return timezone.localtime(self.date_time).time()

    def get_hours_end(self):
        return (timezone.localtime(self.date_time) + timedelta(
            minutes=self.time_range)).time()

    def appointment_exist(self):
        # Usado na hora de criar um appointment avulso com status já agendado
        # Marcando appointment como agendado
        # Verificar se existe outro appointment
        appointments = Appointment.objects.filter(
            company=self.company,
            date_time__date=self.date_time.date(),
            date_time__time__range=(
                timezone.localtime(self.date_time).time(),
                timezone.localtime(self.date_time +
                                   timedelta(minutes=self.time_range)
                                   ).time()
            ),
            status=self.SCHEDULED
        )

        return appointments.count() > 0
