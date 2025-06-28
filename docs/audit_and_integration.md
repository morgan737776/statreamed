# Аудит и интеграция в МИС

## 1. Аудит действий пользователей (AuditLog)
- Все действия в админке, API, интеграциях фиксируются в модели `AuditLog`.
- Примеры действий: просмотр ЭМК, экспорт отчетов, изменение справочников, отправка данных в ЕГИСЗ/ОМС.
- Для REST API и интеграций используйте:
```python
from auditlog.models import LogEntry as AuditLog
AuditLog.objects.log_create(
    actor=request.user,
    action='название_действия',
    remote_addr=request.META.get('REMOTE_ADDR')
)
```

## 2. Аудит интеграций (IntegrationLog)
- Все обмены с внешними системами (ЕГИСЗ, ОМС, шлюзы) фиксируются в `IntegrationLog`.
- Новые поля: `user`, `operation`, `status`, `timestamp`, `request_data`, `response_data`, `error`.
- Пример записи:
```python
IntegrationLog.objects.create(
    user=request.user if request.user.is_authenticated else None,
    operation='send_patient',
    request_data=fhir_json,
    response_data=json.dumps(result),
    status='success',
    error='',
    timestamp=timezone.now()
)
```

## 3. Рекомендации по аудиту
- Логируйте все экспорты, импорты, изменения данных, интеграционные вызовы.
- Храните логи не менее 5 лет (требования Росздравнадзора).
- Ограничьте доступ к журналам только для уполномоченных лиц.

## 4. Документация по интеграции
- Описаны все REST API, форматы обмена, примеры сериализации (см. другие файлы docs/).
- Приложите примеры логов и экспортируемых данных для сертификации.
