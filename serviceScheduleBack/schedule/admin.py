from django.contrib import admin

from .models import Schedule, Appointment, Event, CanceledAppointment


admin.site.register(Schedule)
admin.site.register(Appointment)
admin.site.register(Event)
admin.site.register(CanceledAppointment)
