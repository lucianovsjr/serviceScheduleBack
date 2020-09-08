from django.contrib import admin

from .models import Schedule, Appointment, Event


admin.site.register(Schedule)
admin.site.register(Appointment)
admin.site.register(Event)
