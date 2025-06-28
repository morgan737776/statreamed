from celery import shared_task
from django.utils import timezone
from .models import Notification
from .services import send_sms_notification

@shared_task
def send_pending_notifications():
    """
    Отправляет все ожидающие уведомления
    """
    now = timezone.now()
    
    # Получаем все ожидающие уведомления, которые должны быть отправлены сейчас
    pending_notifications = Notification.objects.filter(
        status='PENDING',
        scheduled_time__lte=now
    ).select_related('sms_notification')
    
    for notification in pending_notifications:
        if notification.notification_type == 'SMS' and notification.sms_notification:
            result = send_sms_notification(notification)
            
            if result['success']:
                notification.status = 'SENT'
                notification.sent_time = now
            else:
                notification.status = 'FAILED'
            
            notification.save()

@shared_task
def schedule_daily_reminders():
    """
    Планирует ежедневную отправку напоминаний
    """
    from .services import schedule_appointment_reminders
    
    schedule_appointment_reminders()
