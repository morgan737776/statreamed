from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from .models import AdmissionRequest

@receiver(post_save, sender=AdmissionRequest)
def on_admission_request_status_change(sender, instance, created, **kwargs):
    """
    Отслеживает изменение статуса заявки на госпитализацию.
    Если статус меняется на 'FULFILLED' (Госпитализирован), то статус
    связанного обращения в комиссию меняется на 'COMPLETED' (Завершено).
    """
    # Нас интересуют только обновления, а не создания
    if created:
        return

    # Проверяем, есть ли у нас исходная заявка и изменился ли статус на FULFILLED
    if instance.source_commission_application and instance.status == 'FULFILLED':
        commission_app = instance.source_commission_application
        
        # Проверяем, чтобы не обновлять лишний раз
        if commission_app.status != 'COMPLETED':
            commission_app.status = 'COMPLETED'
            commission_app.save()
            # В Django сигналах нельзя использовать messages framework напрямую,
            # так как у нас нет доступа к объекту request. 
            # Информацию можно логировать или передавать другим способом.
            print(f"Статус заявки комиссии №{commission_app.id} автоматически изменен на 'Завершено'.")
