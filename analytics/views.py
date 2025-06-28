# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rehab_programs.models import RehabilitationProgram, ScheduledActivity
from django.contrib.auth.models import User
from django.db.models import Count
from datetime import datetime
import json
from django.utils.translation import gettext_lazy as _

@login_required
def report_dashboard(request):
    return render(request, 'analytics/dashboard.html', {'title': _("Дашборд отчетов")})

@login_required
def program_intensity_report(request):
    """
    Отчет по интенсивности программ реабилитации.
    Группирует по типу программы (стационар, амбулатория) и показывает
    среднее количество процедур на одного пациента.
    """
    # Создаем словарь для отображения ключей на русские названия
    program_type_map = {key: str(name) for key, name in RehabilitationProgram.PROGRAM_TYPE_CHOICES}

    report_data = RehabilitationProgram.objects.values('program_type').annotate(
        total_procedures=Count('scheduled_activities'),
        total_patients=Count('patient', distinct=True)
    ).filter(total_patients__gt=0).order_by('program_type')

    labels = [program_type_map.get(item['program_type'], item['program_type']) for item in report_data]
    data = [
        (item['total_procedures'] / item['total_patients']) if item['total_patients'] > 0 else 0
        for item in report_data
    ]

    context = {
        'title': _("Отчет по интенсивности программ"),
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'report_title': _("Интенсивность программ"),
        'chart_label': _("Среднее кол-во процедур на пациента"),
    }
    return render(request, 'analytics/program_intensity_report.html', context)

@login_required
def program_effectiveness_report(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    labels = []
    data = []

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Подсчет назначенных процедур, сгруппированных по названию
        report_data = ScheduledActivity.objects.filter(
            scheduled_date__range=(start_date, end_date)
        ).values(
            'activity__name'  # Группируем по названию из связанной модели RehabActivity
        ).annotate(
            activity_count=Count('id')  # Считаем количество для каждой группы
        ).order_by('-activity_count')

        for item in report_data:
            labels.append(item['activity__name'])
            data.append(item['activity_count'])

    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'analytics/program_effectiveness_report.html', context)

@login_required
def specialist_workload_report(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    labels = []
    data = []

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        report_data = User.objects.filter(
            scheduledactivity__scheduled_date__range=(start_date, end_date),
            is_staff=True
        ).annotate(
            activity_count=Count('scheduledactivity')
        ).filter(activity_count__gt=0).order_by('-activity_count')

        for item in report_data:
            labels.append(item.get_full_name() or item.username)
            data.append(item.activity_count)

    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'analytics/specialist_workload_report.html', context)
