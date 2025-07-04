# Generated by Django 5.2.3 on 2025-06-11 17:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=100, verbose_name='Фамилия')),
                ('middle_name', models.CharField(blank=True, max_length=100, verbose_name='Отчество')),
                ('date_of_birth', models.DateField(verbose_name='Дата рождения')),
                ('gender', models.CharField(choices=[('M', 'Мужской'), ('F', 'Женский')], max_length=1, verbose_name='Пол')),
                ('address', models.TextField(verbose_name='Адрес проживания')),
                ('phone_number', models.CharField(blank=True, max_length=20, verbose_name='Номер телефона')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Электронная почта')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления записи')),
                ('curator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='patients', to=settings.AUTH_USER_MODEL, verbose_name='Куратор')),
            ],
            options={
                'verbose_name': 'Пациент',
                'verbose_name_plural': 'Пациенты',
                'ordering': ['last_name', 'first_name'],
            },
        ),
    ]
