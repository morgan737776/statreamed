from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Q
from django.utils import timezone
from .models import ServiceAppointment, ServiceContract, Payment, ServiceItem


class ServicesDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the services module"""
    template_name = 'services/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        thirty_days_ago = today - timezone.timedelta(days=30)
        
        # Get upcoming appointments
        upcoming_appointments = ServiceAppointment.objects.filter(
            appointment_date__gte=today,
            status__in=['scheduled', 'in_progress']
        ).select_related('service', 'client').order_by('appointment_date')[:5]
        
        # Get recent contracts
        recent_contracts = ServiceContract.objects.select_related('client')\
            .order_by('-created_at')[:5]
        
        # Get revenue statistics
        revenue_stats = Payment.objects.aggregate(
            total_revenue=Sum('amount'),
            monthly_revenue=Sum('amount', filter=Q(payment_date__date__gte=thirty_days_ago))
        )
        
        # Get service popularity
        popular_services = ServiceItem.objects.annotate(
            appointment_count=Count('appointments', filter=Q(appointments__status='completed'))
        ).filter(appointment_count__gt=0).order_by('-appointment_count')[:5]
        
        context.update({
            'page_title': 'Панель управления платными услугами',
            'upcoming_appointments': upcoming_appointments,
            'recent_contracts': recent_contracts,
            'total_revenue': revenue_stats.get('total_revenue') or 0,
            'monthly_revenue': revenue_stats.get('monthly_revenue') or 0,
            'popular_services': popular_services,
            'today': today,
        })
        
        return context
