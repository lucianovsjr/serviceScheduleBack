from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Appointment


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
        STATUS_SET = Appointment.BUSY

        if IS_SCHEDULED:
            STATUS_FILTER = Appointment.FREE
        elif IS_CANCELED:
            STATUS_FILTER = Appointment.BUSY
            STATUS_SET = Appointment.FREE
        else:
            STATUS_FILTER = Appointment.SCHEDULED

        appointments = Appointment.objects.filter(
            company=instance.company,
            date_time__date=timezone.localtime(instance.date_time).date(),
            date_time__time__range=(
                timezone.localtime(instance.date_time).time(),
                timezone.localtime((instance.date_time +
                                    timedelta(minutes=instance.time_range))
                                   ).time()
            ),
            status=STATUS_FILTER
        ).exclude(id=instance.id)

        if IS_SCHEDULED or IS_CANCELED:
            for appointment in appointments:
                appointment.status = STATUS_SET
                appointment.save()
        elif appointments:
            instance.status = STATUS_SET
            instance.save()
