# Generated by Django 3.1.1 on 2020-09-11 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0003_auto_20200911_0145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='canceled_at',
            field=models.DateTimeField(null=True),
        ),
    ]