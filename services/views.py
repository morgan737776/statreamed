from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.db.models import Q, Sum, Count, F
from django.db import transaction
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime

from .models import ServiceCategory, ServiceItem, ServiceAppointment, ServiceContract, ContractService, Payment
from .forms import ServiceCategoryForm, ServiceItemForm, ServiceAppointmentForm, ServiceContractForm, PaymentForm

# Service Category Views
class ServiceCategoryListView(LoginRequiredMixin, ListView):
    model = ServiceCategory
    template_name = 'services/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ServiceCategory.objects.annotate(
            service_count=Count('services', distinct=True)
        )
        
        # Apply search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        # Apply filters
        is_active = self.request.GET.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Service Categories')
        return context

class ServiceCategoryDetailView(LoginRequiredMixin, DetailView):
    model = ServiceCategory
    template_name = 'services/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Get services in this category
        services = category.services.all().select_related('category')
        
        # Calculate statistics
        active_services_count = services.filter(is_active=True).count()
        
        # Get recent activity (last 5 activities)
        recent_activity = []
        
        context.update({
            'services': services,
            'active_services_count': active_services_count,
            'recent_activity': recent_activity,
            'page_title': category.name,
        })
        return context

class ServiceCategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ServiceCategory
    form_class = ServiceCategoryForm
    template_name = 'services/category_form.html'
    permission_required = 'services.add_servicecategory'
    success_url = reverse_lazy('services:category_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Category created successfully.'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Add New Category')
        return context

class ServiceCategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ServiceCategory
    form_class = ServiceCategoryForm
    template_name = 'services/category_form.html'
    permission_required = 'services.change_servicecategory'
    
    def get_success_url(self):
        return reverse_lazy('services:category_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Category updated successfully.'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Edit Category')
        return context

class ServiceCategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ServiceCategory
    template_name = 'services/category_confirm_delete.html'
    permission_required = 'services.delete_servicecategory'
    success_url = reverse_lazy('services:category_list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Category deleted successfully.'))
        return response

# Service Item Views
class ServiceItemListView(LoginRequiredMixin, ListView):
    model = ServiceItem
    template_name = 'services/service_list.html'
    context_object_name = 'object_list'  # Changed from 'services'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ServiceItem.objects.select_related('category')
        
        # Filter by category if specified
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Apply search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        # Apply filters
        service_type = self.request.GET.get('service_type')
        if service_type:
            queryset = queryset.filter(service_type=service_type)
            
        is_active = self.request.GET.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        requires_specialist = self.request.GET.get('requires_specialist')
        if requires_specialist is not None:
            queryset = queryset.filter(requires_specialist=requires_specialist.lower() == 'true')
            
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = ServiceCategory.objects.all() # For filters
        context['service_types'] = ServiceItem.SERVICE_TYPE_CHOICES # For filters
        context['page_title'] = _('Services')
        return context
        
        # Add category filter context if filtering by category
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                context['current_category'] = ServiceCategory.objects.get(pk=category_id)
            except ServiceCategory.DoesNotExist:
                pass
                
        return context

class ServiceItemDetailView(LoginRequiredMixin, DetailView):
    model = ServiceItem
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.get_object()
        
        # Get related appointments (upcoming and past)
        now = timezone.now()
        upcoming_appointments = ServiceAppointment.objects.filter(
            service=service,
            appointment_date__gte=now.date(),
            status__in=['scheduled', 'in_progress']
        ).select_related('client', 'specialist').order_by('appointment_date', 'start_time')
        
        past_appointments = ServiceAppointment.objects.filter(
            service=service,
            appointment_date__lt=now.date()
        ).select_related('client', 'specialist').order_by('-appointment_date', '-start_time')[:5]
        
        # Get contracts that include this service
        contracts = ServiceContract.objects.filter(
            contract_services__service=service
        ).distinct().select_related('client').order_by('-created_at')[:5]
        
        context.update({
            'upcoming_appointments': upcoming_appointments,
            'past_appointments': past_appointments,
            'recent_contracts': contracts,
            'page_title': service.name,
        })
        return context

class ServiceItemCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ServiceItem
    form_class = ServiceItemForm
    template_name = 'services/service_form.html'
    permission_required = 'services.add_serviceitem'
    
    def get_success_url(self):
        return reverse_lazy('services:service_detail', kwargs={'pk': self.object.pk})
    
    def get_initial(self):
        initial = super().get_initial()
        # Set default values for new service
        initial.update({
            'is_active': True,
            'requires_specialist': True,
            'service_type': 'consultation',  # Default service type
            'duration': 60,  # Default duration in minutes
            'duration_unit': 'minutes',
        })
        return initial
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('Service created successfully.'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Add New Service')
        return context

class ServiceItemUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ServiceItem
    form_class = ServiceItemForm
    template_name = 'services/service_form.html'
    permission_required = 'services.change_serviceitem'
    
    def get_success_url(self):
        return reverse_lazy('services:service_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Service updated successfully.'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Edit Service')
        return context

class ServiceItemDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ServiceItem
    template_name = 'services/service_confirm_delete.html'
    permission_required = 'services.delete_serviceitem'
    success_url = reverse_lazy('services:service_list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Service deleted successfully.'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Delete Service')
        return context

# Service Appointment Views
class ServiceAppointmentCreateView(LoginRequiredMixin, CreateView):
    model = ServiceAppointment
    form_class = ServiceAppointmentForm
    template_name = 'services/appointment_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def get_initial(self):
        initial = super().get_initial()
        if 'service' in self.request.GET:
            try:
                service = ServiceItem.objects.get(pk=self.request.GET['service'])
                initial['service'] = service
            except (ValueError, ServiceItem.DoesNotExist):
                pass
                
        if 'date' in self.request.GET:
            try:
                date = datetime.strptime(self.request.GET['date'], '%Y-%m-%d').date()
                initial['appointment_date'] = date
            except (ValueError, TypeError):
                pass
                
        initial['status'] = 'scheduled'
        return initial
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('Appointment created successfully.'))
        return response
        
    def get_success_url(self):
        return reverse('services:appointment_detail', kwargs={'pk': self.object.pk})

class ServiceAppointmentDetailView(LoginRequiredMixin, DetailView):
    model = ServiceAppointment
    template_name = 'services/appointment_detail.html'
    context_object_name = 'appointment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Appointment Details')
        return context

class ServiceAppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceAppointment
    form_class = ServiceAppointmentForm
    template_name = 'services/appointment_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Appointment updated successfully.'))
        return response
    
    def get_success_url(self):
        return reverse('services:appointment_detail', kwargs={'pk': self.object.pk})

class ServiceAppointmentCancelView(LoginRequiredMixin, UpdateView):
    model = ServiceAppointment
    fields = []
    template_name = 'services/appointment_confirm_cancel.html'
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.status = 'cancelled'
        self.object.save()
        messages.success(self.request, _('Appointment has been cancelled.'))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('services:appointment_detail', kwargs={'pk': self.object.pk})

class ServiceAppointmentListView(LoginRequiredMixin, ListView):
    model = ServiceAppointment
    template_name = 'services/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ServiceAppointment.objects.select_related(
            'service', 'client', 'specialist'
        )
        
        # Apply date filters
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            queryset = queryset.filter(appointment_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(appointment_date__lte=date_to)
            
        # Apply status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Apply specialist filter
        specialist_id = self.request.GET.get('specialist')
        if specialist_id:
            queryset = queryset.filter(specialist_id=specialist_id)
            
        # Apply service filter
        service_id = self.request.GET.get('service')
        if service_id:
            queryset = queryset.filter(service_id=service_id)
            
        return queryset.order_by('-appointment_date', '-start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Appointments')
        context['services'] = ServiceItem.objects.filter(is_active=True)
        context['specialists'] = get_user_model().objects.filter(
            groups__name='Specialists', is_active=True
        )
        return context

class ServiceAppointmentCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'services/appointment_calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        specialist_id = self.request.GET.get('specialist')
        service_id = self.request.GET.get('service')
        
        # Get base queryset
        appointments = ServiceAppointment.objects.select_related(
            'service', 'client', 'specialist'
        ).filter(
            status__in=['scheduled', 'in_progress']
        )
        
        # Apply filters
        if specialist_id:
            appointments = appointments.filter(specialist_id=specialist_id)
        if service_id:
            appointments = appointments.filter(service_id=service_id)
        
        # Format events for FullCalendar
        events = []
        for appt in appointments:
            events.append({
                'id': appt.id,
                'title': f"{appt.client.get_short_name()} - {appt.service.name}",
                'start': f"{appt.appointment_date.isoformat()}T{appt.start_time.isoformat()}",
                'end': f"{appt.appointment_date.isoformat()}T{appt.end_time.isoformat()}",
                'className': f'fc-event-{appt.status}',
                'extendedProps': {
                    'service': appt.service.name,
                    'specialist': str(appt.specialist) if appt.specialist else 'Не назначен',
                    'status': appt.get_status_display(),
                    'status_class': appt.status,
                }
            })
        
        context.update({
            'page_title': 'Календарь записей',
            'events_json': json.dumps(events, default=str),
            'services': ServiceItem.objects.filter(is_active=True),
            'specialists': get_user_model().objects.filter(
                groups__name='Specialists', is_active=True
            ),
            'selected_specialist': specialist_id,
            'selected_service': service_id,
        })
        return context

# Service Appointment Views

# Service Contract Views
class ServiceContractListView(LoginRequiredMixin, ListView):
    model = ServiceContract
    template_name = 'services/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ServiceContract.objects.select_related('client')
        
        # Apply filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        client = self.request.GET.get('client')
        if client:
            queryset = queryset.filter(
                Q(client__first_name__icontains=client) |
                Q(client__last_name__icontains=client) |
                Q(client__email__icontains=client)
            )
            
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(start_date__gte=date_from)
            
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(end_date__lte=date_to)
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Service Contracts')
        return context


class ServiceContractDetailView(LoginRequiredMixin, DetailView):
    model = ServiceContract
    template_name = 'services/contract_detail.html'
    context_object_name = 'contract'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Contract Details')
        return context


class ServiceContractCreateView(LoginRequiredMixin, CreateView):
    model = ServiceContract
    form_class = ServiceContractForm
    template_name = 'services/contract_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('Contract created successfully.'))
        return response
    
    def get_success_url(self):
        return reverse('services:contract_detail', kwargs={'pk': self.object.pk})


class ServiceContractUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceContract
    form_class = ServiceContractForm
    template_name = 'services/contract_form.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Contract updated successfully.'))
        return response
    
    def get_success_url(self):
        return reverse('services:contract_detail', kwargs={'pk': self.object.pk})


class ServiceContractPrintView(LoginRequiredMixin, DetailView):
    model = ServiceContract
    template_name = 'services/contract_print.html'
    context_object_name = 'contract'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Print Contract')
        return context


class ServiceContractEmailView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        contract = get_object_or_404(ServiceContract, pk=kwargs['pk'])
        # TODO: Implement email sending logic
        messages.success(request, _('Contract has been sent via email.'))
        return redirect('services:contract_detail', pk=contract.pk)


# Payment Views
class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'services/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Payment.objects.select_related('contract', 'contract__client')
        
        # Apply filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        payment_method = self.request.GET.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
            
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(payment_date__gte=date_from)
            
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(payment_date__lte=date_to)
            
        return queryset.order_by('-payment_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Payments')
        return context


class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'services/payment_detail.html'
    context_object_name = 'payment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Payment Details')
        return context


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'services/payment_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        contract_id = self.request.GET.get('contract')
        if contract_id:
            try:
                contract = ServiceContract.objects.get(pk=contract_id)
                initial['contract'] = contract
                initial['amount'] = contract.balance_due
            except (ValueError, ServiceContract.DoesNotExist):
                pass
        return initial
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('Payment recorded successfully.'))
        return response
    
    def get_success_url(self):
        return reverse('services:payment_detail', kwargs={'pk': self.object.pk})


class PaymentReceiptView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'services/payment_receipt.html'
    context_object_name = 'payment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Payment Receipt')
        return context


class PaymentEmailView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        payment = get_object_or_404(Payment, pk=kwargs['pk'])
        # TODO: Implement email sending logic
        payment.receipt_sent = True
        payment.save(update_fields=['receipt_sent'])
        messages.success(request, _('Payment receipt has been sent via email.'))
        return redirect('services:payment_detail', pk=payment.pk)


# Report Views
class ServiceReportView(LoginRequiredMixin, TemplateView):
    template_name = 'services/reports/service_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from query parameters
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        # Filter services
        services = ServiceItem.objects.all()
        
        # Apply date filters to appointments
        appointments = ServiceAppointment.objects.all()
        if date_from:
            appointments = appointments.filter(appointment_date__gte=date_from)
        if date_to:
            appointments = appointments.filter(appointment_date__lte=date_to)
        
        # Calculate service usage statistics
        service_stats = []
        for service in services:
            service_appointments = appointments.filter(service=service)
            service_stats.append({
                'service': service,
                'appointment_count': service_appointments.count(),
                'total_revenue': service_appointments.aggregate(
                    total=Sum('service__price')
                )['total'] or 0,
            })
        
        context.update({
            'page_title': _('Service Usage Report'),
            'service_stats': service_stats,
            'date_from': date_from,
            'date_to': date_to,
        })
        return context


class PaymentReportView(LoginRequiredMixin, TemplateView):
    template_name = 'services/reports/payment_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from query parameters
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        # Filter payments
        payments = Payment.objects.select_related('contract', 'contract__client')
        
        if date_from:
            payments = payments.filter(payment_date__gte=date_from)
        if date_to:
            payments = payments.filter(payment_date__lte=date_to)
        
        # Calculate payment statistics
        total_payments = payments.aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # Group by payment method
        payment_methods = payments.values('payment_method').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        context.update({
            'page_title': _('Payment Report'),
            'payments': payments,
            'total_amount': total_payments['total'] or 0,
            'total_count': total_payments['count'] or 0,
            'payment_methods': payment_methods,
            'date_from': date_from,
            'date_to': date_to,
        })
        return context


class ContractReportView(LoginRequiredMixin, TemplateView):
    template_name = 'services/reports/contract_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from query parameters
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        # Filter contracts
        contracts = ServiceContract.objects.select_related('client')
        
        if date_from:
            contracts = contracts.filter(created_at__gte=date_from)
        if date_to:
            contracts = contracts.filter(created_at__lte=date_to)
        
        # Calculate contract statistics
        contract_stats = contracts.aggregate(
            total_amount=Sum('total_amount'),
            total_final=Sum('final_amount'),
            count=Count('id'),
            avg_amount=Avg('total_amount'),
        )
        
        context.update({
            'page_title': _('Contract Report'),
            'contracts': contracts,
            'total_amount': contract_stats['total_amount'] or 0,
            'total_final': contract_stats['total_final'] or 0,
            'contract_count': contract_stats['count'] or 0,
            'avg_amount': contract_stats['avg_amount'] or 0,
            'date_from': date_from,
            'date_to': date_to,
        })
        return context



# Add API views for AJAX requests
def services_by_category(request):
    """API endpoint to get services by category ID"""
    from django.http import JsonResponse
    from .models import ServiceItem
    
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'error': 'Category ID is required'}, status=400)
        
    services = ServiceItem.objects.filter(
        category_id=category_id,
        is_active=True
    ).values('id', 'name', 'price')
    
    return JsonResponse({
        'services': list(services)
    })


def get_available_slots(request):
    """API endpoint to get available time slots for a service"""
    service_id = request.GET.get('service_id')
    date = request.GET.get('date')
    
    # TODO: Implement actual slot availability logic
    # This is a placeholder implementation
    available_slots = [
        '09:00', '10:00', '11:00', '14:00', '15:00', '16:00'
    ]
    
    return JsonResponse({'slots': available_slots})

@require_http_methods(["POST"])
def calculate_service_price(request):
    """API endpoint to calculate service price with discounts"""
    # TODO: Implement price calculation logic
    return JsonResponse({'status': 'success', 'price': 0})

def generate_contract_pdf(request, pk):
    """Generate PDF for a service contract"""
    # TODO: Implement PDF generation
    from django.http import HttpResponse
    return HttpResponse("PDF generation not implemented yet")
