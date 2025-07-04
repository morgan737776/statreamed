# Generated by Django 5.2.3 on 2025-06-20 10:36

from django.db import migrations


def create_specializations(apps, schema_editor):
    Specialization = apps.get_model('core', 'Specialization')

    specializations = [
        # Реабилитация и терапия
        'Физиотерапевт',
        'Врач по лечебной физкультуре (ЛФК)',
        'Эрготерапевт',
        'Массажист',
        'Мануальный терапевт',
        'Кинезиотерапевт',
        # Врачи-специалисты
        'Невролог',
        'Кардиолог',
        'Ортопед-травматолог',
        'Пульмонолог',
        'Ревматолог',
        'Эндокринолог',
        'Гастроэнтеролог',
        'Терапевт',
        'Гериатр',
        # Психологическая и речевая поддержка
        'Клинический психолог',
        'Нейропсихолог',
        'Психотерапевт',
        'Логопед-афазиолог',
        # Диагностика
        'Врач ультразвуковой диагностики (УЗИ)',
        'Врач функциональной диагностики (ЭКГ, ЭЭГ)',
        'Рентгенолог',
        # Консультанты и прочее
        'Диетолог',
        'Социальный работник',
        'Специалист по протезированию',
    ]

    for spec_name in specializations:
        Specialization.objects.get_or_create(name=spec_name)



class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_create_default_groups'),
    ]

    operations = [
        migrations.RunPython(create_specializations),
    ]
