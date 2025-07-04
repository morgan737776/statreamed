# Generated by Django 5.2.3 on 2025-06-19 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rehab_programs', '0006_populate_rehab_activities'),
    ]

    operations = [
        migrations.CreateModel(
            name='RehabProgramTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название шаблона программы')),
                ('description', models.TextField(blank=True, verbose_name='Описание программы')),
                ('program_type', models.CharField(choices=[('INPATIENT', 'Стационарная'), ('OUTPATIENT', 'Амбулаторная'), ('HOME_BASED', 'На дому')], max_length=20, verbose_name='Форма реабилитации')),
                ('activities', models.ManyToManyField(blank=True, to='rehab_programs.rehabactivity', verbose_name='Процедуры в шаблоне')),
            ],
            options={
                'verbose_name': 'Шаблон программы реабилитации',
                'verbose_name_plural': 'Шаблоны программ реабилитации',
                'ordering': ['name'],
            },
        ),
    ]
