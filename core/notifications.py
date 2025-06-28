from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_appointment_confirmation_email(appointment):
    """
    Sends a confirmation email to the client after an appointment is created.
    """
    client = appointment.client
    if not client or not client.user.email:
        # Cannot send email if the client has no email address.
        return

    subject = 'Подтверждение записи на прием'
    client_name = client.user.get_full_name() or client.user.username
    
    context = {
        'appointment': appointment,
        'client_name': client_name,
    }

    # Render both plain text and HTML versions of the email
    text_content = render_to_string('core/email/appointment_confirmation.txt', context)
    html_content = render_to_string('core/email/appointment_confirmation.html', context)

    send_mail(
        subject=subject,
        message=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
        recipient_list=[client.user.email],
        html_message=html_content,
        fail_silently=False, # Set to True in production to avoid crashing on email errors
    )

def send_appointment_reminder_email(appointment):
    """
    Sends a reminder email to the client for an upcoming appointment.
    """
    client = appointment.client
    if not client or not client.user.email:
        return

    subject = 'Напоминание о записи на прием'
    client_name = client.user.get_full_name() or client.user.username

    context = {
        'appointment': appointment,
        'client_name': client_name,
    }

    text_content = render_to_string('core/email/appointment_reminder.txt', context)
    html_content = render_to_string('core/email/appointment_reminder.html', context)

    send_mail(
        subject=subject,
        message=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
        recipient_list=[client.user.email],
        html_message=html_content,
        fail_silently=False,
    )
