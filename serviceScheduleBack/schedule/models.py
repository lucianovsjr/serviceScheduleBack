from django.db import models


class Schedule(models.Model):
    provider = models.ForeignKey('access.Perfil', on_delete=models.CASCADE)
    date_start = models.DateField('Data inicial')
    date_end = models.DateField('Data final')
    hours_start = models.TimeField('Hora inicial')
    hours_end = models.TimeField('Hora Final')
    time_range = models.IntegerField('Tempo de atendimento', default=0)


class Appointment(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    provider = models.ForeignKey('access.Perfil', verbose_name='Provider', on_delete=models.CASCADE, related_name='appointment_provider')
    user = models.ForeignKey('access.Perfil', verbose_name='Usuário', on_delete=models.CASCADE, related_name='appointment_user')
    date = models.DateField('Data')
    hour = models.TimeField('Hora')
    canceled_at = models.DateTimeField()
    loose_client = models.CharField('Cliente avulso', max_length=30)
    time_range = models.IntegerField('Tempo de atendimento', default=0)

    def available(self):
        return not self.user


class Event(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField('Nome', max_length=30)
    week = models.CharField('Semana', max_length=7)
    date = models.DateField('Data')
    hours_start = models.TimeField('Hora inicial')
    hours_end = models.TimeField('Hora Final')
    all_day = models.BooleanField('Todo dia', default=False)
