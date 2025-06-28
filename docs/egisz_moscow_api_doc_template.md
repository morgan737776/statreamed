# Документация по интеграции с ЕГИСЗ Москвы

## 1. Описание архитектуры
- Взаимодействие через REST API FHIR (Patient, Encounter, ServiceRequest)
- Авторизация по OAuth2 (client_credentials)
- Передача сообщений по HTTPS с ГОСТ-шифрованием (при необходимости)

## 2. Параметры подключения
- API URL: `https://egisz.mos.ru/api/fhir/`
- Token URL: `https://egisz.mos.ru/api/auth/token/`
- Client ID/Secret: выдаются ДИТ Москвы

## 3. Примеры FHIR-ресурсов
### Patient
```json
{
  "resourceType": "Patient",
  "id": "123",
  "name": [{"family": "Иванов", "given": ["Иван"]}],
  "birthDate": "1980-01-01",
  "identifier": [
    {"system": "urn:oid:1.2.643.5.1.13.13.12.2.21.1", "value": "123-456-789 00"},
    {"system": "urn:egisz:moscow:oms", "value": "1234567890123456"}
  ]
}
```
### Encounter (госпитализация)
```json
{
  "resourceType": "Encounter",
  "id": "456",
  "status": "in-progress",
  "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP"},
  "subject": {"reference": "Patient/123"},
  "period": {"start": "2025-06-15T09:00:00+03:00"}
}
```
### ServiceRequest (услуга)
```json
{
  "resourceType": "ServiceRequest",
  "id": "789",
  "status": "active",
  "intent": "order",
  "subject": {"reference": "Patient/123"},
  "code": {"coding": [{"system": "urn:egisz:moscow:service", "code": "A01.01.001"}]}
}
```

## 4. Логирование и аудит
- Все запросы и ответы сохраняются в IntegrationLog с указанием региона `moscow` и correlation_id

## 5. Требования по безопасности
- Использовать российские сертификаты УЦ
- Хранить client_secret в .env
- Вести журнал интеграции для Росздравнадзора Москвы
