# Generated by Django 5.2.3 on 2025-06-12 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commissions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selectioncommitteeapplication',
            name='appointment_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Назначенная дата и время заседания'),
        ),
    ]
