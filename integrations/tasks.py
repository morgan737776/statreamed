from celery import shared_task
import logging

from .services_remd import RemdService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_document_to_remd_task(self, entry_id):
    """Асинхронная задача для отправки медицинского документа в РЭМД."""
    # Импортируем модель здесь, чтобы избежать циклического импорта
    from emr.models import MedicalRecordEntry
    
    try:
        logger.info(f"Запуск задачи отправки в РЭМД для записи {entry_id}")
        entry = MedicalRecordEntry.objects.get(id=entry_id)
        
        # Проверяем, нужно ли отправлять документ
        if entry.remd_status == 'sent':
            logger.warning(f"Документ {entry_id} уже был отправлен в РЭМД. Пропуск.")
            return

        entry.remd_status = 'processing'
        entry.save(update_fields=['remd_status'])

        remd_service = RemdService()
        document_id = remd_service.send_document(entry)

        # Обновляем статус в случае успеха
        entry.remd_status = 'sent'
        entry.remd_document_id = document_id
        entry.save(update_fields=['remd_status', 'remd_document_id'])
        logger.info(f"Задача для записи {entry_id} успешно завершена. ID документа в РЭМД: {document_id}")

    except MedicalRecordEntry.DoesNotExist:
        logger.error(f"Запись с ID {entry_id} не найдена. Задача не может быть выполнена.")
    except Exception as exc:
        logger.error(f"Ошибка при отправке документа {entry_id} в РЭМД: {exc}")
        entry.remd_status = 'failed'
        entry.save(update_fields=['remd_status'])
        # Повторяем попытку, если не превышен лимит
        raise self.retry(exc=exc)
