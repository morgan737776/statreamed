import requests
from datetime import datetime
from django.conf import settings
from .models import Notification, SMSNotification

def send_sms_notification(notification: Notification) -> dict:
    """
    Отправляет SMS уведомление через провайдера
    """
    sms_notification = notification.sms_notification
    
    # Настройки провайдера SMS
    provider_settings = settings.SMS_PROVIDERS.get(sms_notification.sms_provider, {})
    
    # Формируем сообщение
    message = notification.message
    if notification.notification_type == 'APPOINTMENT':
        message = f"Напоминание о приеме: {message}"
    
    try:
        # Пример отправки через провайдера SMS
        response = requests.post(
            provider_settings.get('api_url'),
            headers={
                'Authorization': f'Bearer {provider_settings.get('api_key')}',
                'Content-Type': 'application/json'
            },
            json={
                'to': sms_notification.phone_number,
                'message': message,
                'from': provider_settings.get('sender_id', 'CLINIC')
            }
        )
        
        response.raise_for_status()
        
        # Обновляем статус уведомления
        notification.status = 'SENT'
        notification.sent_time = datetime.now()
        notification.save()
        
        sms_notification.provider_response = response.json()
        sms_notification.save()
        
        return {'success': True, 'message': 'SMS успешно отправлено'}
        
    except requests.exceptions.RequestException as e:
        notification.status = 'FAILED'
        notification.save()
        
        sms_notification.provider_response = str(e)
        sms_notification.save()
        
        return {'success': False, 'error': str(e)}

def schedule_appointment_reminders():
    """
    Планирует отправку напоминаний о приемах за 24 часа до начала
    """
    from core.models import Appointment
    
    # Получаем приемы, которые начнутся через 24 часа
    tomorrow = datetime.now() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        start_datetime__date=tomorrow.date(),
        start_datetime__hour=tomorrow.hour,
        start_datetime__minute=tomorrow.minute
    )
    
    for appointment in appointments:
        # Создаем уведомление
        notification = Notification.objects.create(
            patient=appointment.patient,
            title='Напоминание о приеме',
            message=f'Завтра в {appointment.start_datetime.strftime("%H:%M")} у вас прием с {appointment.doctor.get_full_name()}',
            notification_type='REMINDER',
            scheduled_time=tomorrow - timedelta(hours=24)
        )
        
        # Создаем SMS уведомление
        SMSNotification.objects.create(
            notification=notification,
            phone_number=appointment.patient.phone_number,
            sms_provider=settings.DEFAULT_SMS_PROVIDER
        )
