# Generated by Django 3.1.1 on 2020-09-16 01:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedule', '0005_auto_20200914_2339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='canceled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='loose_client',
            field=models.CharField(blank=True, max_length=30, verbose_name='Cliente avulso'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_user', to=settings.AUTH_USER_MODEL, verbose_name='Usuário'),
        ),
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(null=True, verbose_name='Data'),
        ),
    ]
