from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import date, timedelta

from .notifications import send_appointment_reminder_email

logger = get_task_logger(__name__)


@shared_task
def send_appointment_reminders():
    """
    Находит все подтвержденные записи на следующий день и отправляет напоминания.
    """
    from .models import ServiceAppointment
    tomorrow = date.today() + timedelta(days=1)
    appointments_to_remind = ServiceAppointment.objects.filter(
        appointment_date=tomorrow,
        status='scheduled' # Only remind for scheduled appointments
    )

    logger.info(f"Found {appointments_to_remind.count()} appointments for tomorrow ({tomorrow}). Sending reminders...")

    for appointment in appointments_to_remind:
        try:
            logger.info(f"Sending reminder for appointment ID: {appointment.id} to {appointment.client.user.email}")
            send_appointment_reminder_email(appointment)
        except Exception as e:
            logger.error(f"Failed to send reminder for appointment ID {appointment.id}: {e}")

    return f"Reminder task completed. Sent {appointments_to_remind.count()} reminders."
