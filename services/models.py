from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid
import os

User = get_user_model()

def contract_upload_path(instance, filename):
    return f'contracts/{instance.contract_number}/{filename}'

class ServiceCategory(models.Model):
    """Category for paid services (e.g., Medical, Rehabilitation, Diagnostics)"""
    name = models.CharField(_('Category Name'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Service Category')
        verbose_name_plural = _('Service Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

class ServiceItem(models.Model):
    """Individual paid service that can be offered to clients"""
    SERVICE_TYPE_CHOICES = [
        ('consultation', _('Consultation')),
        ('procedure', _('Procedure')),
        ('diagnostic', _('Diagnostic')),
        ('therapy', _('Therapy')),
        ('other', _('Other')),
    ]
    
    DURATION_UNIT_CHOICES = [
        ('minutes', _('Minutes')),
        ('hours', _('Hours')),
        ('days', _('Days')),
    ]

    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name='services')
    name = models.CharField(_('Service Name'), max_length=200)
    code = models.CharField(_('Service Code'), max_length=50, unique=True, help_text=_('Internal service code'))
    description = models.TextField(_('Description'), blank=True)
    service_type = models.CharField(_('Service Type'), max_length=20, choices=SERVICE_TYPE_CHOICES)
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    duration = models.PositiveIntegerField(_('Duration'), help_text=_('Duration of the service'))
    duration_unit = models.CharField(_('Duration Unit'), max_length=10, choices=DURATION_UNIT_CHOICES, default='minutes')
    is_active = models.BooleanField(_('Active'), default=True)
    requires_specialist = models.BooleanField(_('Requires Specialist'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Service Item')
        verbose_name_plural = _('Service Items')
        ordering = ['category__name', 'name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['service_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()}) - {self.price} ₽"

    def get_duration_display(self):
        return f"{self.duration} {self.get_duration_unit_display()}"

class ServiceAppointment(models.Model):
    """Scheduled appointment for a paid service"""
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
    ]

    appointment_number = models.CharField(_('Appointment #'), max_length=20, unique=True, editable=False)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_appointments')
    service = models.ForeignKey(ServiceItem, on_delete=models.PROTECT, related_name='appointments')
    specialist = models.ForeignKey(User, on_delete=models.PROTECT, related_name='service_schedule',
                                 limit_choices_to={'groups__name': 'Specialists'})
    appointment_date = models.DateField(_('Appointment Date'))
    start_time = models.TimeField(_('Start Time'))
    end_time = models.TimeField(_('End Time'), blank=True, null=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # Поля для интеграции с телемедициной (Zoom)
    is_telemedicine = models.BooleanField(_('Телемедицинская консультация'), default=False)
    zoom_meeting_id = models.CharField(_('ID встречи Zoom'), max_length=255, blank=True, null=True)
    zoom_start_url = models.URLField(_('URL для начала встречи (врач)'), max_length=1024, blank=True, null=True)
    zoom_join_url = models.URLField(_('URL для подключения (пациент)'), max_length=1024, blank=True, null=True)

    notes = models.TextField(_('Notes'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Service Appointment')
        verbose_name_plural = _('Service Appointments')
        ordering = ['-appointment_date', 'start_time']
        indexes = [
            models.Index(fields=['appointment_date', 'start_time']),
            models.Index(fields=['client']),
            models.Index(fields=['specialist']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.appointment_number} - {self.client.get_full_name()} - {self.service.name}"

    def save(self, *args, **kwargs):
        if not self.appointment_number:
            self.appointment_number = f"SRV-{timezone.now().strftime('%Y%m%d')}-{ServiceAppointment.objects.count() + 1:04d}"
        super().save(*args, **kwargs)

class ServiceContract(models.Model):
    """Contract for paid services"""
    CONTRACT_STATUS = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('terminated', _('Terminated')),
    ]

    contract_number = models.CharField(_('Contract #'), max_length=20, unique=True, editable=False)
    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='service_contracts')
    status = models.CharField(_('Status'), max_length=20, choices=CONTRACT_STATUS, default='draft')
    start_date = models.DateField(_('Start Date'), default=timezone.now)
    end_date = models.DateField(_('End Date'), blank=True, null=True)
    total_amount = models.DecimalField(_('Total Amount'), max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(_('Discount'), max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(_('Tax Rate %'), max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('Tax Amount'), max_digits=12, decimal_places=2, default=0)
    final_amount = models.DecimalField(_('Final Amount'), max_digits=12, decimal_places=2, default=0)
    terms = models.TextField(_('Terms and Conditions'), blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    contract_file = models.FileField(_('Contract File'), upload_to=contract_upload_path, blank=True, null=True)
    signed_at = models.DateTimeField(_('Signed At'), blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contracts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Service Contract')
        verbose_name_plural = _('Service Contracts')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contract_number} - {self.client.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.contract_number:
            self.contract_number = f"CON-{timezone.now().strftime('%Y%m%d')}-{ServiceContract.objects.count() + 1:04d}"
        
        # Calculate amounts
        self.tax_amount = (self.total_amount - self.discount) * (self.tax_rate / 100)
        self.final_amount = (self.total_amount - self.discount) + self.tax_amount
        
        super().save(*args, **kwargs)

class ContractService(models.Model):
    """Services included in a contract"""
    contract = models.ForeignKey(ServiceContract, on_delete=models.CASCADE, related_name='contract_services')
    service = models.ForeignKey(ServiceItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2)
    discount = models.DecimalField(_('Discount'), max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(_('Total Price'), max_digits=12, decimal_places=2, editable=False)
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        verbose_name = _('Contract Service')
        verbose_name_plural = _('Contract Services')

    def __str__(self):
        return f"{self.service.name} x{self.quantity} - {self.total_price} ₽"

    def save(self, *args, **kwargs):
        self.total_price = (self.unit_price * self.quantity) - self.discount
        super().save(*args, **kwargs)
        # Update contract total amount
        self.contract.total_amount = sum(cs.total_price for cs in self.contract.contract_services.all())
        self.contract.save()

class Payment(models.Model):
    """Payments for services"""
    PAYMENT_METHODS = [
        ('cash', _('Cash')),
        ('card', _('Credit/Debit Card')),
        ('bank_transfer', _('Bank Transfer')),
        ('online', _('Online Payment')),
        ('insurance', _('Insurance')),
    ]

    PAYMENT_STATUS = [
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
        ('partially_refunded', _('Partially Refunded')),
    ]

    contract = models.ForeignKey(ServiceContract, on_delete=models.PROTECT, related_name='payments')
    payment_number = models.CharField(_('Payment #'), max_length=20, unique=True, editable=False)
    amount = models.DecimalField(_('Amount'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_method = models.CharField(_('Payment Method'), max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(_('Status'), max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(_('Transaction ID'), max_length=100, blank=True)
    payment_date = models.DateTimeField(_('Payment Date'), default=timezone.now)
    notes = models.TextField(_('Notes'), blank=True)
    receipt_sent = models.BooleanField(_('Receipt Sent'), default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.payment_number} - {self.amount} ₽ - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = f"PAY-{timezone.now().strftime('%Y%m%d')}-{Payment.objects.count() + 1:04d}"
        super().save(*args, **kwargs)

    def send_receipt(self, request=None):
        """Send payment receipt to client"""
        if not self.receipt_sent and self.status == 'completed':
            subject = f"Квитанция об оплате {self.payment_number}"
            context = {
                'payment': self,
                'contract': self.contract,
                'client': self.contract.client,
            }
            
            message = render_to_string('services/emails/payment_receipt.txt', context, request)
            html_message = render_to_string('services/emails/payment_receipt.html', context, request)
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.contract.client.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            self.receipt_sent = True
            self.save(update_fields=['receipt_sent'])
            return True
        return False
