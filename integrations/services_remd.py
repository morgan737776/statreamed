import requests
import logging
import uuid
import os
import json
import time
import base64
import hashlib
from typing import Tuple, Dict, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

# Django imports
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.core.cache import cache
from django.conf import settings

# XML processing
from lxml import etree
from signxml import DigestAlgorithm
from signxml.xades import XAdESSigner, XAdESVerifier

# Local imports
from .models import RemdSettings, RemdDocumentLog
from core.models import Patient, MedicalRecord
from core.cache_optimization import cached_function

# Configure logger
logger = logging.getLogger('integrations.remd')

# Константы для РЭМД
REMD_TIMEOUT = 30  # Seconds
RETRY_COUNT = 3    # Number of retries
RETRY_DELAY = 5    # Seconds between retries

class RemdService:
    """Сервис для взаимодействия с РЭМД."""

    def __init__(self, force_settings_reload=False):
        """
        Инициализация сервиса РЭМД с поддержкой кэширования конфигурации
        
        Args:
            force_settings_reload (bool): Принудительно загрузить настройки из БД
        """
        self.settings = self._get_settings(force_reload=force_settings_reload)
        if not self.settings or not self.settings.is_active:
            logger.error("Интеграция с РЭМД не настроена или не активна.")
            raise ImproperlyConfigured("Интеграция с РЭМД не настроена или не активна.")
        
        # Инициализация свойств для хранения сертификата и ключа
        self._cert_content = None
        self._key_content = None
        self._last_token_refresh = None
        self._auth_token = None
    
    @cached_function(timeout=3600, prefix='remd_settings')
    def _get_settings(self, force_reload=False):
        """
        Получает настройки РЭМД из базы данных или из кэша
        
        Args:
            force_reload (bool): Если True, перезагружает настройки из БД
            
        Returns:
            RemdSettings: Объект настроек для РЭМД
        """
        cache_key = 'remd_settings'
        if force_reload:
            cache.delete(cache_key)
            
        try:
            return RemdSettings.objects.select_related('organization').first()
        except Exception as e:
            logger.error(f"Ошибка при получении настроек РЭМД: {e}")
            return None
            
    def _get_certificate(self):
        """
        Получает содержимое сертификата. Кэширует для повторного использования.
        
        Returns:
            bytes: Содержимое сертификата
        """
        if not self._cert_content:
            try:
                with open(self.settings.certificate_path, 'rb') as f:
                    self._cert_content = f.read()
            except FileNotFoundError as e:
                logger.error(f"Сертификат не найден по пути {self.settings.certificate_path}: {e}")
                raise
            except Exception as e:
                logger.error(f"Ошибка чтения сертификата: {e}")
                raise
        return self._cert_content
    
    def _get_private_key(self):
        """
        Получает содержимое приватного ключа. Кэширует для повторного использования.
        
        Returns:
            bytes: Содержимое приватного ключа
        """
        if not self._key_content:
            try:
                with open(self.settings.private_key_path, 'rb') as f:
                    self._key_content = f.read()
            except FileNotFoundError as e:
                logger.error(f"Приватный ключ не найден по пути {self.settings.private_key_path}: {e}")
                raise
            except Exception as e:
                logger.error(f"Ошибка чтения приватного ключа: {e}")
                raise
        return self._key_content
        
    def _get_auth_token(self, force_refresh=False):
        """
        Получает токен аутентификации для РЭМД, при необходимости обновляет его
        
        Args:
            force_refresh (bool): Принудительно получить новый токен
            
        Returns:
            str: Токен аутентификации
        """
        # Проверяем необходимость обновления токена
        if (not self._auth_token or force_refresh or 
           (self._last_token_refresh and 
            datetime.now() - self._last_token_refresh > timedelta(hours=1))):
            self._auth_token = self._refresh_auth_token()
            self._last_token_refresh = datetime.now()
            
        return self._auth_token
    
    def _refresh_auth_token(self):
        """
        Обновляет токен аутентификации через API РЭМД
        
        Returns:
            str: Новый токен аутентификации
        """
        # В реальной имплементации здесь должен быть код для получения токена
        # по API интеграции с РЭМД
        logger.info("Получение нового токена аутентификации для РЭМД...")
        
        # Для демонстрации возвращаем заглушку
        return f"demo_token_{uuid.uuid4()}"

    def _generate_cda_xml(self, entry, document_id=None):
        """
        Генерирует CDA XML документ на основе медицинской записи с помощью шаблона Jinja2.
        
        Args:
            entry: Медицинская запись
            document_id: Опциональный ID документа. Если не указан, генерируется новый UUID
            
        Returns:
            str: XML-строка с CDA документом
        """
        logger.info(f"Генерация CDA XML для записи ID: {entry.id}")
        start_time = time.time()
        
        try:
            # 1. Получаем настройки и связанные объекты с предварительной загрузкой для снижения количества запросов к БД
            patient = entry.medical_record.patient
            
            # Проверяем, есть ли у врача связанный Staff объект
            author_user = entry.doctor
            try:
                author_staff = author_user.staff  # Получаем связанный объект Staff
            except AttributeError:
                logger.warning(f"У врача ID:{author_user.id} отсутствует связанный Staff объект. Используем данные пользователя.")
                # Создаем временный объект с данными пользователя для шаблона
                author_staff = type('StaffStub', (), {
                    'id': author_user.id,
                    'last_name': getattr(author_user, 'last_name', ''),
                    'first_name': getattr(author_user, 'first_name', ''),
                    'patronymic': getattr(author_user, 'patronymic', '')
                })
            
            # Используем кэшированные настройки
            settings = self.settings

            # 2. Подготавливаем контекст для шаблона с обработкой потенциально отсутствующих данных
            document_id = document_id or str(uuid.uuid4())
            
            # Формируем контекст для рендеринга шаблона с проверкой полей
            context = {
                'document_id': document_id,
                'medical_org_oid': settings.organization_oid,
                'document_type_code': '1',  # Пример, нужно определить по справочнику
                'document_type_name': 'Протокол консультации',
                'document_title': f'Медицинская запись №{entry.id}',
                'creation_time': datetime.utcnow().strftime('%Y%m%d%H%M%S'),
                'patient': {
                    'id': patient.id,
                    'last_name': patient.last_name or '',
                    'first_name': patient.first_name or '',
                    'middle_name': getattr(patient, 'patronymic', '') or '',
                    'gender_code': patient.gender or 'U',  # 'M', 'F' или 'U' (неизвестно)
                    'gender_name': self._get_gender_name(patient.gender),
                    'birth_date': patient.date_of_birth.strftime('%Y%m%d') if patient.date_of_birth else '',
                    'address': getattr(patient, 'address', '') or '',
                },
                'author': {
                    'id': author_staff.id,
                    'last_name': author_staff.last_name or '',
                    'first_name': author_staff.first_name or '',
                    'middle_name': getattr(author_staff, 'patronymic', '') or '',
                    'position': getattr(author_staff, 'position', '') or 'Врач',
                },
                'organization': {
                    'name': settings.organization_name,
                    'oid': settings.organization_oid,
                    'address': getattr(settings, 'organization_address', '') or '',
                },
                'entry': {
                    'id': entry.id,
                    'date': entry.created_at.strftime('%Y%m%d%H%M%S') if hasattr(entry, 'created_at') else datetime.utcnow().strftime('%Y%m%d%H%M%S'),
                    'text_content': entry.text_content or '',
                    'diagnosis_code': getattr(entry, 'diagnosis_code', '') or '',
                    'diagnosis_name': getattr(entry, 'diagnosis_name', '') or '',
                }
            }

            # 3. Рендерим шаблон с обработкой потенциальных ошибок
            try:
                xml_content = render_to_string('integrations/remd/cda_document.xml', context)
                # Проверяем качество сгенерированного XML
                try:
                    etree.fromstring(xml_content.encode('utf-8'))
                except Exception as xml_error:
                    logger.warning(f"Сгенерированный XML имеет проблемы со структурой: {xml_error}")
                    # Пытаемся исправить проблемы с XML
                    xml_content = self._fix_xml_issues(xml_content)
                
                execution_time = time.time() - start_time
                logger.info(f"XML сгенерирован успешно за {execution_time:.2f} сек.")
                return xml_content
            except Exception as template_error:
                logger.error(f"Ошибка при рендеринге шаблона CDA: {template_error}")
                raise
                
        except Exception as e:
            logger.error(f"Неожиданная ошибка при генерации CDA XML: {e}")
            raise
    
    def _get_gender_name(self, gender_code):
        """
        Получает текстовое представление пола по коду
        
        Args:
            gender_code: Код пола ('M', 'F' или другой)
            
        Returns:
            str: Текстовое представление пола
        """
        gender_mapping = {
            'M': 'Мужской',
            'F': 'Женский',
            'm': 'Мужской',
            'f': 'Женский',
            '1': 'Мужской',
            '2': 'Женский',
        }
        return gender_mapping.get(gender_code, 'Не указан')
    
    def _fix_xml_issues(self, xml_content):
        """
        Пытается исправить распространенные проблемы с XML
        
        Args:
            xml_content: Исходный XML
            
        Returns:
            str: Исправленный XML
        """
        # Заменяем недопустимые символы
        xml_content = xml_content.replace('&', '&amp;')
        
        # Проверяем корректность закрытия тегов
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
            return etree.tostring(root, encoding='unicode', pretty_print=True)
        except Exception:
            # Если не удалось исправить, возвращаем исходный контент
            return xml_content

    def _sign_xml(self, xml_string):
        """
        Подписывает XML-строку с использованием XAdES-BES подписи.
        
        Args:
            xml_string: XML-строка для подписи
            
        Returns:
            str: Подписанная XML-строка
        
        Raises:
            ValueError: При неверных входных данных
            IOError: При ошибках доступа к файлам сертификатов
            Exception: При других ошибках
        """
        start_time = time.time()
        logger.info("Подписание CDA XML...")
        
        # Проверяем входные данные
        if not xml_string or not isinstance(xml_string, str):
            error_msg = f"Неправильный формат XML для подписи: {type(xml_string)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Используем кэшированные методы получения сертификата и ключа
        try:
            cert = self._get_certificate()
            key = self._get_private_key()
            
            # Создаем пароль ключа если необходимо
            password = None
            if self.settings.private_key_password:
                password = self.settings.private_key_password.encode('utf-8')

            # Инициализируем подписывающий модуль с обработкой исключений
            try:
                signer = XAdESSigner(c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#")
                signed_root = signer.sign(
                    xml_string.encode('utf-8'),
                    key=key,
                    cert=cert,
                    key_passphrase=password
                )
                
                # Преобразуем подписанный XML в строку
                signed_xml_string = etree.tostring(signed_root, encoding='unicode')
                
                # Логируем успешное подписание и затраченное время
                execution_time = time.time() - start_time
                logger.info(f"XML успешно подписан за {execution_time:.2f} сек.")
                return signed_xml_string
                
            except Exception as sign_error:
                logger.error(f"Ошибка при подписании XML: {sign_error}")
                # Проверяем, не связана ли ошибка с проблемами в самом XML
                try:
                    # Проверяем, может ли XML быть парсен
                    etree.fromstring(xml_string.encode('utf-8'))
                    # Если мы дошли сюда, XML формат корректный, но есть другая проблема
                    raise sign_error  # Передаем ошибку дальше
                except etree.XMLSyntaxError as xml_error:
                    # Проблема с форматом XML
                    logger.error(f"Ошибка в формате XML: {xml_error}")
                    raise ValueError(f"Некорректный XML: {xml_error}") from sign_error

        except FileNotFoundError as e:
            error_msg = f"Ошибка подписания: файл ключа или сертификата не найден - {e}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
        except Exception as e:
            logger.error(f"Неожиданная ошибка при подписании XML: {e}")
            raise

    def send_document(self, medical_entry):
        """Основной метод для отправки медицинского документа в РЭМД."""
        if not self.settings.api_url:
            raise ImproperlyConfigured("URL API для РЭМД не указан в настройках.")

        # 1. Сгенерировать CDA XML
        cda_xml = self._generate_cda_xml(medical_entry)

        # 2. Подписать XML
        signed_xml = self._sign_xml(cda_xml)
        if not signed_xml:
            return None, "Signing failed"

        # 3. Отправить в РЭМД (временно отключено, используется заглушка)
        logger.info(f"Отправка подписанного CDA XML в РЭМД для записи {medical_entry.id}...")

        # --- Начало блока реальной отправки (закомментировано) ---
        # headers = {
        #     'Content-Type': 'application/xml; charset=utf-8',
        #     'Authorization': f'Bearer {self.settings.auth_token}' # Если требуется токен
        # }
        #
        # try:
        #     response = requests.post(
        #         self.settings.api_url,
        #         data=signed_xml.encode('utf-8'),
        #         headers=headers,
        #         timeout=30
        #     )
        #     response.raise_for_status()
        #     response_data = response.json()
        #     document_id = response_data.get('document_id')
        #     logger.info(f"Документ успешно отправлен в РЭМД. ID: {document_id}")
        #     return document_id, "Success"
        # except requests.exceptions.RequestException as e:
        #     logger.error(f"Ошибка при отправке документа в РЭМД: {e}")
        #     return None, str(e)
        # --- Конец блока реальной отправки ---

        # Временная заглушка для имитации успешного ответа
        document_id = str(uuid.uuid4())
        status_message = "Отправлено (заглушка)"
        logger.info(f"Имитация успешной отправки. Document ID: {document_id}")
        return document_id, status_message
