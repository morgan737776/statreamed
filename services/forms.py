from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import (
    ServiceCategory, ServiceItem, ServiceAppointment,
    ServiceContract, ContractService, Payment
)

User = get_user_model()

class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = ServiceItem
        fields = [
            'name', 'code', 'category', 'service_type', 'price', 
            'duration', 'duration_unit', 'description', 
            'is_active', 'requires_specialist'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
            'code': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
            'category': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
            'service_type': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
            'price': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
            'duration': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
            'duration_unit': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
            'requires_specialist': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ServiceCategory.objects.filter(is_active=True)

class ServiceAppointmentForm(forms.ModelForm):
    class Meta:
        model = ServiceAppointment
        fields = [
            'client', 'service', 'specialist',
            'appointment_date', 'start_time', 'end_time',
            'status', 'notes'
        ]
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Filter active services
        self.fields['service'].queryset = ServiceItem.objects.filter(is_active=True)
        
        # Filter specialists
        self.fields['specialist'].queryset = User.objects.filter(
            groups__name='Specialists', is_active=True
        )
        
        # Set initial values
        if not self.instance.pk:
            self.fields['status'].initial = 'scheduled'
            self.fields['appointment_date'].initial = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        appointment_date = cleaned_data.get('appointment_date')
        specialist = cleaned_data.get('specialist')
        service = cleaned_data.get('service')
        
        # Check if end time is after start time
        if start_time and end_time and end_time <= start_time:
            self.add_error('end_time', _('End time must be after start time'))
        
        # Check if specialist is available
        if specialist and appointment_date and start_time and end_time:
            conflicting_appointments = ServiceAppointment.objects.filter(
                specialist=specialist,
                appointment_date=appointment_date,
                status__in=['scheduled', 'in_progress'],
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            for appt in conflicting_appointments:
                if (start_time < appt.end_time and end_time > appt.start_time):
                    self.add_error(
                        None,
                        _(f'Specialist is already booked from {appt.start_time} to {appt.end_time}')
                    )
                    break
        
        return cleaned_data

class ServiceContractForm(forms.ModelForm):
    class Meta:
        model = ServiceContract
        fields = [
            'client', 'status', 'start_date', 'end_date',
            'discount', 'tax_rate', 'terms', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'terms': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['status'].initial = 'draft'
            self.fields['start_date'].initial = timezone.now().date()

class ContractServiceForm(forms.ModelForm):
    class Meta:
        model = ContractService
        fields = ['service', 'quantity', 'unit_price', 'discount', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = ServiceItem.objects.filter(is_active=True)
        
        # Set initial unit price from service if available
        if self.instance and self.instance.service:
            self.fields['unit_price'].initial = self.instance.service.price
        elif 'service' in self.data:
            try:
                service_id = int(self.data.get('service'))
                service = ServiceItem.objects.get(id=service_id)
                self.fields['unit_price'].initial = service.price
            except (ValueError, ServiceItem.DoesNotExist):
                pass

ContractServiceFormSet = inlineformset_factory(
    ServiceContract, ContractService,
    form=ContractServiceForm,
    extra=1,
    can_delete=True
)

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'contract', 'amount', 'payment_method',
            'status', 'transaction_id', 'payment_date', 'notes'
        ]
        widgets = {
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contract'].queryset = ServiceContract.objects.all()
        
        if not self.instance.pk:
            self.fields['status'].initial = 'pending'
            self.fields['payment_date'].initial = timezone.now()
    
    def clean(self):
        cleaned_data = super().clean()
        contract = cleaned_data.get('contract')
        amount = cleaned_data.get('amount')
        
        if contract and amount:
            # Calculate remaining amount on contract
            total_paid = Payment.objects.filter(
                contract=contract,
                status='completed'
            ).exclude(pk=self.instance.pk if self.instance else None).aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            remaining_amount = contract.final_amount - total_paid
            
            if amount > remaining_amount:
                self.add_error(
                    'amount',
                    _(f'Amount exceeds remaining contract balance. Maximum: {remaining_amount:.2f} руб.')
                )
        
        return cleaned_data
