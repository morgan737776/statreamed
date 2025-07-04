# Generated by Django 5.2.3 on 2025-06-12 16:07

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_specialization_specialistprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название палаты')),
                ('department', models.CharField(blank=True, max_length=100, verbose_name='Отделение')),
                ('floor', models.PositiveSmallIntegerField(default=1, verbose_name='Этаж')),
                ('capacity', models.PositiveSmallIntegerField(default=1, verbose_name='Вместимость')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'Палата',
                'verbose_name_plural': 'Палаты',
                'ordering': ['department', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Bed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20, verbose_name='Номер койки')),
                ('bed_type', models.CharField(choices=[('standard', 'Стандартная'), ('intensive', 'Интенсивная терапия'), ('post_op', 'Послеоперационная'), ('isolation', 'Изоляционная')], default='standard', max_length=50, verbose_name='Тип койки')),
                ('is_available', models.BooleanField(default=True, verbose_name='Доступна')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('ward', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ward', verbose_name='Палата')),
            ],
            options={
                'verbose_name': 'Койка',
                'verbose_name_plural': 'Койки',
                'ordering': ['ward__name', 'number'],
                'unique_together': {('ward', 'number')},
            },
        ),
        migrations.CreateModel(
            name='PatientAdmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admission_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата поступления')),
                ('discharge_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата выписки')),
                ('diagnosis', models.TextField(blank=True, verbose_name='Диагноз при поступлении')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('bed', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='patientadmission', to='core.bed', verbose_name='Койка')),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admitted_patients', to=settings.AUTH_USER_MODEL, verbose_name='Лечащий врач')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admissions', to='core.patient', verbose_name='Пациент')),
            ],
            options={
                'verbose_name': 'Госпитализация',
                'verbose_name_plural': 'Госпитализации',
                'ordering': ['-admission_date'],
                'indexes': [models.Index(fields=['admission_date'], name='core_patien_admissi_ff8e91_idx'), models.Index(fields=['discharge_date'], name='core_patien_dischar_4ca1de_idx')],
            },
        ),
    ]
