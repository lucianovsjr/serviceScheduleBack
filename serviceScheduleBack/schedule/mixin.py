from .models import Appointment


def appointments_schedule_exists(date_start, date_end, time_start, time_end):
    appointments = Appointment.objects.filter(
        date_time__date__range=(date_start, date_end),
        date_time__time__range=(time_start, time_end)
    )
    
    return appointments.count() == 0
