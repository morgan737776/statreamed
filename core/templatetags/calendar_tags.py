from django import template
from datetime import datetime, timedelta
import calendar

register = template.Library()

@register.simple_tag
def get_calendar(date):
    """
    Возвращает данные календаря для отображения в шаблоне
    """
    cal = calendar.monthcalendar(date.year, date.month)
    
    # Преобразуем числа в объекты datetime для удобства
    weeks = []
    for week in cal:
        week_days = []
        for day in week:
            if day == 0:
                # Пустой день (не принадлежит текущему месяцу)
                week_days.append(None)
            else:
                # Создаем объект datetime для текущего дня
                day_date = datetime(date.year, date.month, day)
                week_days.append(day_date)
        weeks.append(week_days)
    
    return {
        'weeks': weeks,
        'month': date.month,
        'year': date.year
    }

@register.filter
def get_item(dictionary, key):
    """
    Фильтр для получения значения из словаря по ключу
    """
    if dictionary is None:
        return None
    
    # Преобразуем ключ в int, если это строка
    if isinstance(key, str):
        try:
            key = int(key)
        except (ValueError, TypeError):
            pass
    
    return dictionary.get(key)
