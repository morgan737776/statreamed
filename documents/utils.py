from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext as _


def send_document_status_email(document, new_status, to_email):
    """
    Отправляет email-уведомление о смене статуса документа.
    """
    status_map = {
        'draft': _('Черновик'),
        'pending_approval': _('Ожидает утверждения'),
        'approved': _('Утверждён'),
        'archived': _('Архивирован'),
    }
    subject = f"Документ: '{document.title}' — новый статус: {status_map.get(new_status, new_status)}"
    message = render_to_string('documents/email/document_status_changed.txt', {
        'document': document,
        'status': status_map.get(new_status, new_status),
    })
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=True,
    )
