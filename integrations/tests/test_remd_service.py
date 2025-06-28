# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from unittest.mock import patch, mock_open, MagicMock
from datetime import date
import tempfile
import os

from core.models import Patient, Doctor
from medical_history.models import MedicalRecord
from integrations.models import RemdSettings
from integrations.services_remd import RemdService


class RemdServiceTest(TestCase):
    """Тесты для сервиса интеграции с РЭМД"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        # Создаем временные файлы для сертификатов
        self.cert_file = tempfile.NamedTemporaryFile(delete=False)
        self.key_file = tempfile.NamedTemporaryFile(delete=False)
        
        self.cert_file.write(b'test certificate content')
        self.key_file.write(b'test private key content')
        
        self.cert_file.close()
        self.key_file.close()
        
        # Создаем настройки РЭМД
        self.remd_settings = RemdSettings.objects.create(
            api_url='https://test-remd.api.com',
            organization_oid='1.2.3.4.5',
            certificate_path=self.cert_file.name,
            private_key_path=self.key_file.name,
            private_key_password='test_password',
            is_active=True
        )
        
        # Создаем тестовые данные
        self.user = User.objects.create_user(
            username='test_doctor',
            first_name='Доктор',
            last_name='Тестовый'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.user,
            specialization='Терапевт',
            license_number='DOC123456'
        )
        
        self.patient = Patient.objects.create(
            first_name='Иван',
            last_name='Пациент',
            patronymic='Тестович',
            date_of_birth=date(1990, 1, 1),
            gender='M',
            snils='123-456-789 01',
            passport_series='1234',
            passport_number='567890'
        )
        
        self.medical_record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis='Тестовый диагноз',
            treatment_plan='Тестовый план лечения',
            recommendations='Тестовые рекомендации'
        )
    
    def tearDown(self):
        """Очистка после тестов"""
        # Удаляем временные файлы
        os.unlink(self.cert_file.name)
        os.unlink(self.key_file.name)
    
    def test_remd_service_initialization_success(self):
        """Тест успешной инициализации сервиса РЭМД"""
        service = RemdService()
        
        self.assertEqual(service.settings, self.remd_settings)
        self.assertEqual(service.api_url, 'https://test-remd.api.com')
        self.assertEqual(service.organization_oid, '1.2.3.4.5')
    
    def test_remd_service_initialization_no_settings(self):
        """Тест инициализации без настроек РЭМД"""
        # Удаляем настройки
        RemdSettings.objects.all().delete()
        
        with self.assertRaises(ImproperlyConfigured) as context:
            RemdService()
        
        self.assertIn('Настройки для интеграции с РЭМД не найдены', str(context.exception))
    
    def test_remd_service_initialization_inactive_settings(self):
        """Тест инициализации с неактивными настройками"""
        self.remd_settings.is_active = False
        self.remd_settings.save()
        
        with self.assertRaises(ImproperlyConfigured) as context:
            RemdService()
        
        self.assertIn('Интеграция с РЭМД не настроена или не активна', str(context.exception))
    
    def test_get_certificate_cached(self):
        """Тест кэширования сертификата"""
        service = RemdService()
        
        # Первый вызов должен читать файл
        cert1 = service._get_certificate()
        self.assertEqual(cert1, b'test certificate content')
        
        # Второй вызов должен вернуть кэшированное значение
        cert2 = service._get_certificate()
        self.assertEqual(cert2, cert1)
    
    def test_get_private_key_cached(self):
        """Тест кэширования приватного ключа"""
        service = RemdService()
        
        # Первый вызов должен читать файл
        key1 = service._get_private_key()
        self.assertEqual(key1, b'test private key content')
        
        # Второй вызов должен вернуть кэшированное значение
        key2 = service._get_private_key()
        self.assertEqual(key2, key1)
    
    def test_get_certificate_file_not_found(self):
        """Тест обработки отсутствующего файла сертификата"""
        self.remd_settings.certificate_path = '/nonexistent/path/cert.pem'
        self.remd_settings.save()
        
        service = RemdService()
        
        with self.assertRaises(FileNotFoundError):
            service._get_certificate()
    
    def test_get_private_key_file_not_found(self):
        """Тест обработки отсутствующего файла приватного ключа"""
        self.remd_settings.private_key_path = '/nonexistent/path/key.pem'
        self.remd_settings.save()
        
        service = RemdService()
        
        with self.assertRaises(FileNotFoundError):
            service._get_private_key()
    
    def test_get_gender_name_male(self):
        """Тест получения названия пола для мужчины"""
        service = RemdService()
        
        gender_name = service._get_gender_name('M')
        self.assertEqual(gender_name, 'Мужской')
    
    def test_get_gender_name_female(self):
        """Тест получения названия пола для женщины"""
        service = RemdService()
        
        gender_name = service._get_gender_name('F')
        self.assertEqual(gender_name, 'Женский')
    
    def test_get_gender_name_unknown(self):
        """Тест получения названия пола для неизвестного значения"""
        service = RemdService()
        
        gender_name = service._get_gender_name('X')
        self.assertEqual(gender_name, 'Не указан')
    
    @patch('integrations.services_remd.render_to_string')
    def test_generate_cda_xml_success(self, mock_render):
        """Тест успешной генерации CDA XML"""
        service = RemdService()
        
        # Мокируем render_to_string
        mock_render.return_value = '<ClinicalDocument>Test XML</ClinicalDocument>'
        
        xml_content = service._generate_cda_xml(self.medical_record)
        
        self.assertEqual(xml_content, '<ClinicalDocument>Test XML</ClinicalDocument>')
        
        # Проверяем, что render_to_string был вызван с правильными параметрами
        mock_render.assert_called_once()
        args, kwargs = mock_render.call_args
        
        self.assertEqual(args[0], 'integrations/remd/cda_document.xml')
        self.assertIn('patient', kwargs['context'])
        self.assertIn('doctor', kwargs['context'])
        self.assertIn('medical_record', kwargs['context'])
    
    @patch('integrations.services_remd.render_to_string')
    def test_generate_cda_xml_with_missing_patient(self, mock_render):
        """Тест генерации CDA XML с отсутствующим пациентом"""
        service = RemdService()
        
        # Создаем медицинскую запись без пациента
        medical_record_no_patient = MedicalRecord(
            doctor=self.doctor,
            diagnosis='Тест без пациента'
        )
        
        mock_render.return_value = '<ClinicalDocument>Test XML</ClinicalDocument>'
        
        xml_content = service._generate_cda_xml(medical_record_no_patient)
        
        self.assertEqual(xml_content, '<ClinicalDocument>Test XML</ClinicalDocument>')
        
        # Проверяем, что в контексте patient будет None
        args, kwargs = mock_render.call_args
        self.assertIsNone(kwargs['context']['patient'])
    
    @patch('integrations.services_remd.XAdESSigner')
    @patch('integrations.services_remd.etree')
    def test_sign_xml_success(self, mock_etree, mock_signer_class):
        """Тест успешного подписания XML"""
        service = RemdService()
        
        # Настраиваем моки
        mock_signer = MagicMock()
        mock_signer_class.return_value = mock_signer
        
        mock_signed_root = MagicMock()
        mock_signer.sign.return_value = mock_signed_root
        
        mock_etree.tostring.return_value = '<SignedDocument>Signed XML</SignedDocument>'
        
        xml_string = '<ClinicalDocument>Test XML</ClinicalDocument>'
        signed_xml = service._sign_xml(xml_string)
        
        self.assertEqual(signed_xml, '<SignedDocument>Signed XML</SignedDocument>')
        
        # Проверяем, что signer был вызван с правильными параметрами
        mock_signer.sign.assert_called_once_with(
            xml_string.encode('utf-8'),
            key=b'test private key content',
            cert=b'test certificate content',
            key_passphrase=b'test_password'
        )
    
    def test_sign_xml_invalid_input(self):
        """Тест подписания XML с невалидными входными данными"""
        service = RemdService()
        
        # Тестируем с пустой строкой
        with self.assertRaises(ValueError) as context:
            service._sign_xml('')
        
        self.assertIn('Неправильный формат XML', str(context.exception))
        
        # Тестируем с None
        with self.assertRaises(ValueError) as context:
            service._sign_xml(None)
        
        self.assertIn('Неправильный формат XML', str(context.exception))
    
    @patch('integrations.services_remd.requests.post')
    def test_send_to_remd_success(self, mock_post):
        """Тест успешной отправки документа в РЭМД"""
        service = RemdService()
        
        # Настраиваем мок ответа
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'document_id': 'DOC123456',
            'message': 'Документ успешно принят'
        }
        mock_post.return_value = mock_response
        
        signed_xml = '<SignedDocument>Signed XML</SignedDocument>'
        result = service._send_to_remd(signed_xml)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['document_id'], 'DOC123456')
        
        # Проверяем параметры запроса
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        
        self.assertEqual(args[0], 'https://test-remd.api.com/api/v1/documents')
        self.assertIn('timeout', kwargs)
        self.assertEqual(kwargs['timeout'], 30)
    
    @patch('integrations.services_remd.requests.post')
    def test_send_to_remd_server_error(self, mock_post):
        """Тест обработки ошибки сервера при отправке в РЭМД"""
        service = RemdService()
        
        # Настраиваем мок ответа с ошибкой
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_post.return_value = mock_response
        
        signed_xml = '<SignedDocument>Signed XML</SignedDocument>'
        result = service._send_to_remd(signed_xml)
        
        self.assertFalse(result['success'])
        self.assertIn('Ошибка сервера РЭМД', result['error'])
    
    @patch('integrations.services_remd.requests.post')
    def test_send_to_remd_connection_error(self, mock_post):
        """Тест обработки ошибки соединения при отправке в РЭМД"""
        service = RemdService()
        
        # Настраиваем мок для генерации исключения
        mock_post.side_effect = Exception('Connection failed')
        
        signed_xml = '<SignedDocument>Signed XML</SignedDocument>'
        result = service._send_to_remd(signed_xml)
        
        self.assertFalse(result['success'])
        self.assertIn('Connection failed', result['error'])


class RemdIntegrationTest(TestCase):
    """Интеграционные тесты для РЭМД"""
    
    def setUp(self):
        """Подготовка данных для интеграционных тестов"""
        # Создаем временные файлы
        self.cert_file = tempfile.NamedTemporaryFile(delete=False)
        self.key_file = tempfile.NamedTemporaryFile(delete=False)
        
        self.cert_file.write(b'integration test certificate')
        self.key_file.write(b'integration test private key')
        
        self.cert_file.close()
        self.key_file.close()
        
        # Создаем настройки
        self.remd_settings = RemdSettings.objects.create(
            api_url='https://integration-test-remd.api.com',
            organization_oid='1.2.3.4.5.6',
            certificate_path=self.cert_file.name,
            private_key_path=self.key_file.name,
            is_active=True
        )
        
        # Создаем полные тестовые данные
        self.user = User.objects.create_user(
            username='integration_doctor',
            first_name='Интеграционный',
            last_name='Доктор'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.user,
            specialization='Интеграционный тест',
            license_number='INT123456'
        )
        
        self.patient = Patient.objects.create(
            first_name='Интеграционный',
            last_name='Пациент',
            patronymic='Тестович',
            date_of_birth=date(1985, 6, 15),
            gender='M',
            snils='987-654-321 01',
            passport_series='9876',
            passport_number='543210'
        )
        
        self.medical_record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis='Интеграционный диагноз',
            treatment_plan='Интеграционный план лечения',
            recommendations='Интеграционные рекомендации'
        )
    
    def tearDown(self):
        """Очистка после интеграционных тестов"""
        os.unlink(self.cert_file.name)
        os.unlink(self.key_file.name)
    
    @patch('integrations.services_remd.render_to_string')
    @patch('integrations.services_remd.XAdESSigner')
    @patch('integrations.services_remd.etree')
    @patch('integrations.services_remd.requests.post')
    def test_full_integration_workflow(self, mock_post, mock_etree, mock_signer_class, mock_render):
        """Тест полного рабочего процесса интеграции с РЭМД"""
        service = RemdService()
        
        # Настраиваем все моки
        mock_render.return_value = '<ClinicalDocument>Integration Test XML</ClinicalDocument>'
        
        mock_signer = MagicMock()
        mock_signer_class.return_value = mock_signer
        mock_signed_root = MagicMock()
        mock_signer.sign.return_value = mock_signed_root
        
        mock_etree.tostring.return_value = '<SignedDocument>Integration Signed XML</SignedDocument>'
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'document_id': 'INTEGRATION_DOC_123',
            'message': 'Интеграционный документ успешно принят'
        }
        mock_post.return_value = mock_response
        
        # Выполняем полный цикл отправки документа
        result = service.send_medical_record(self.medical_record)
        
        # Проверяем результат
        self.assertTrue(result['success'])
        self.assertEqual(result['document_id'], 'INTEGRATION_DOC_123')
        
        # Проверяем, что все этапы были выполнены
        mock_render.assert_called_once()
        mock_signer.sign.assert_called_once()
        mock_etree.tostring.assert_called_once()
        mock_post.assert_called_once()
