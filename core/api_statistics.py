from rest_framework import views, response
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Appointment, Patient
from services.models import ServiceCategory
from django.db.models.functions import ExtractYear, ExtractMonth

class StatisticsView(views.APIView):
    def get(self, request):
        # Получаем текущую дату и начало месяца
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Финансовая статистика
        total_income = Appointment.objects.filter(
            start_datetime__gte=start_of_month
        ).aggregate(Sum('price'))['price__sum'] or 0
        
        average_check = Appointment.objects.filter(
            start_datetime__gte=start_of_month
        ).aggregate(Avg('price'))['price__avg'] or 0
        
        # Количество пациентов
        total_patients = Patient.objects.count()
        new_patients = Patient.objects.filter(
            created_at__gte=start_of_month
        ).count()
        
        # Распределение по возрасту
        age_distribution = [
            Patient.objects.filter(age__range=(0, 18)).count(),
            Patient.objects.filter(age__range=(19, 35)).count(),
            Patient.objects.filter(age__range=(36, 50)).count(),
            Patient.objects.filter(age__range=(51, 65)).count(),
            Patient.objects.filter(age__gt=65).count()
        ]
        
        # Распределение по полу
        gender_distribution = [
            Patient.objects.filter(gender='M').count(),
            Patient.objects.filter(gender='F').count()
        ]
        
        # Распределение по услугам
        services = ServiceModel.objects.all()
        services_distribution = {
            'labels': [service.name for service in services],
            'values': [
                Appointment.objects.filter(
                    start_datetime__gte=start_of_month,
                    service=service
                ).count() for service in services
            ]
        }
        
        return response.Response({
            'total_income': total_income,
            'average_check': average_check,
            'total_patients': total_patients,
            'new_patients': new_patients,
            'age_distribution': age_distribution,
            'gender_distribution': gender_distribution,
            'services_distribution': services_distribution
        })
