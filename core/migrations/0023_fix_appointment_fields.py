from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_alter_appointment_options_remove_appointment_all_day_and_more'),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='service',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='services.serviceitem',
                verbose_name='Услуга',
                default=1  # Укажите ID существующей услуги или удалите default, если не нужно
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appointment',
            name='price',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name='Цена'
            ),
        ),
        migrations.AddField(
            model_name='appointment',
            name='notes',
            field=models.TextField(blank=True, verbose_name='Примечания'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активен'),
        ),
    ]
