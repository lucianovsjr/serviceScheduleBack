from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Appointment, CanceledAppointment


def canceled_appointment(instance):
    canceled = CanceledAppointment(
        provider=instance.provider,
        time_range=instance.time_range,
        date_time=instance.date_time,
        schedule=instance.schedule,
        company=instance.company,
        user=instance.user,
        canceled_at=instance.canceled_at,
        loose_client=instance.loose_client
    )
    canceled.save()


@receiver(post_save, sender=Appointment)
def save_appointment(sender, instance, **kwargs):
    '''
    Quando criar um agendamento o horário deve estar livre,
    caso não esteja, ficara como ocupado.
    Ao agendar um horário todos os outros horários devem ficar ocupados.
    Cancelamento de horário todos os outros que foram ocupados por este
    devem ficar livres.
    '''

    if not instance.status == Appointment.BUSY:
        IS_FREE = instance.status == Appointment.FREE
        IS_CANCELED = IS_FREE and instance.canceled_at is not None
        IS_SCHEDULED = instance.status == Appointment.SCHEDULED
        status_set = Appointment.BUSY
        provider_set = None

        if IS_SCHEDULED:
            STATUS_FILTER = Appointment.FREE
            provider_set = instance.provider
        elif IS_CANCELED:
            STATUS_FILTER = Appointment.BUSY
            status_set = Appointment.FREE
            provider_set = instance.provider_busy
        else:
            STATUS_FILTER = Appointment.SCHEDULED

        appointments = Appointment.objects.filter(
            company=instance.company,
            date_time__date=timezone.localtime(instance.date_time).date(),
            date_time__time__range=(
                timezone.localtime(instance.date_time).time(),
                timezone.localtime((instance.date_time +
                                    timedelta(minutes=instance.time_range-1))
                                   ).time()
            ),
            status=STATUS_FILTER
        ).exclude(id=instance.id)

        if IS_SCHEDULED or IS_CANCELED:
            for appointment in appointments:
                appointment.status = status_set
                appointment.provider_busy = provider_set
                appointment.send_notification = True
                appointment.save()
        elif appointments:
            instance.status = status_set
            instance.provider_busy = provider_set
            instance.send_notification = True
            instance.save()

        if IS_CANCELED:
            canceled_appointment(instance)
