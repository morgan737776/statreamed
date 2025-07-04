# Generated by Django 5.2.3 on 2025-06-20 10:39

from django.db import migrations


def create_document_categories(apps, schema_editor):
    DocumentCategory = apps.get_model('documents', 'DocumentCategory')

    categories = [
        # Личные документы пациента
        'Паспорт',
        'Полис ОМС/ДМС',
        'СНИЛС',
        'Свидетельство о рождении',
        'Справка об инвалидности (МСЭ)',

        # Входящие медицинские документы
        'Направление на реабилитацию (форма 057/у)',
        'Выписка из амбулаторной карты',
        'Предыдущие выписные эпикризы',
        'Результаты анализов (лабораторные)',
        'Результаты исследований (МРТ, КТ, УЗИ)',
        'Результаты функциональной диагностики (ЭКГ, ЭЭГ)',

        # Внутренние медицинские документы
        'Первичный осмотр врача',
        'Индивидуальная программа реабилитации (ИПР)',
        'План лечения',
        'Лист врачебных назначений',
        'Дневник наблюдений',
        'Заключения консультантов',
        'Выписной эпикриз',
        'Больничный лист',

        # Юридические и финансовые документы
        'Договор на оказание платных медицинских услуг',
        'Информированное добровольное согласие',
        'Согласие на обработку персональных данных',
        'Счет на оплату',
        'Чек / Квитанция об оплате',
    ]

    for category_name in categories:
        DocumentCategory.objects.get_or_create(name=category_name)



class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0005_documentversion'),
    ]

    operations = [
        migrations.RunPython(create_document_categories),
    ]
