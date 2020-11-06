from django.apps import AppConfig


class ScheduleConfig(AppConfig):
    name = 'serviceScheduleBack.schedule'

    def ready(sef):
        import serviceScheduleBack.schedule.signals
