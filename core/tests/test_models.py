# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta

from core.models import Patient, Staff, Appointment, SystemSettings, PatientDocument, MedicalRecord

# Пробуем импортировать ServiceItem, если доступен
try:
    from services.models import ServiceItem
except ImportError:
    ServiceItem = None


class PatientModelTest(TestCase):
    def setUp(self):
        self.patient_data = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'middle_name': 'Сергеевич',
            'date_of_birth': date(1990, 5, 15),
            'gender': 'M',
            'phone': '+7(903)123-45-67',
            'email': 'ivan.petrov@example.com',
            'address': 'г. Москва, ул. Тверская, д. 1',
            'passport_series': '1234',
            'passport_number': '567890',
            'insurance_policy': '1234567890123456'
        }

    def test_patient_creation(self):
        """Тест создания пациента"""
        patient = Patient.objects.create(**self.patient_data)
        
        self.assertEqual(patient.first_name, 'Иван')
        self.assertEqual(patient.last_name, 'Петров')
        self.assertEqual(patient.middle_name, 'Сергеевич')
        self.assertEqual(patient.gender, 'M')
        self.assertEqual(patient.phone, '+7(903)123-45-67')
        self.assertEqual(patient.email, 'ivan.petrov@example.com')

    def test_patient_str_representation(self):
        """Тест строкового представления пациента"""
        patient = Patient.objects.create(**self.patient_data)
        expected_str = "Петров Иван Сергеевич"
        self.assertEqual(str(patient), expected_str)

    def test_patient_get_full_name(self):
        """Тест метода get_full_name"""
        patient = Patient.objects.create(**self.patient_data)
        expected_name = "Петров Иван Сергеевич"
        self.assertEqual(patient.get_full_name(), expected_name)

    def test_patient_without_middle_name(self):
        """Тест пациента без отчества"""
        data = self.patient_data.copy()
        data['middle_name'] = ''
        data['email'] = 'ivan.petrov2@example.com'
        patient = Patient.objects.create(**data)
        expected_str = "Петров Иван"
        self.assertEqual(str(patient), expected_str)

    def test_patient_unique_email(self):
        """Тест что email может быть не уникальным"""
        Patient.objects.create(**self.patient_data)
        
        # Создаем второго пациента с тем же email - должно работать
        data = self.patient_data.copy()
        data['first_name'] = 'Анна'
        data['last_name'] = 'Иванова'
        patient2 = Patient.objects.create(**data)
        
        # Проверяем что оба пациента созданы
        self.assertEqual(Patient.objects.count(), 2)


class StaffModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff_user',
            first_name='Доктор',
            last_name='Врачев',
            email='staff@example.com'
        )
        
        self.staff_data = {
            'first_name': 'Анна',
            'last_name': 'Врачева',
            'middle_name': 'Ивановна',
            'position': 'Терапевт',
            'department': 'Поликлиника',
            'email': 'anna.vracheva@example.com',
            'phone': '+7(903)456-78-90',
            'status': 'active',
            'user': self.user,
            'hire_date': date.today()
        }

    def test_staff_creation(self):
        """Тест создания сотрудника"""
        staff = Staff.objects.create(**self.staff_data)
        
        self.assertEqual(staff.first_name, 'Анна')
        self.assertEqual(staff.last_name, 'Врачева')
        self.assertEqual(staff.position, 'Терапевт')
        self.assertEqual(staff.status, 'active')

    def test_staff_str_representation(self):
        """Тест строкового представления сотрудника"""
        staff = Staff.objects.create(**self.staff_data)
        expected_str = "Врачева Анна Ивановна"
        self.assertEqual(str(staff), expected_str)


class AppointmentModelTest(TestCase):
    def setUp(self):
        # Создаем пациента
        self.patient = Patient.objects.create(
            first_name='Анна',
            last_name='Петрова',
            date_of_birth=date(1985, 5, 15),
            gender='F',
            email='anna.petrova@example.com',
            phone='+7(903)123-45-67',
            address='г. Москва, ул. Тверская, д. 1',
            passport_series='1234',
            passport_number='567890',
            insurance_policy='1234567890123456'
        )
        
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='test_doctor',
            first_name='Доктор',
            last_name='Врачев',
            email='doctor@example.com'
        )
        
        # Создаем Staff для doctor поля
        self.staff = Staff.objects.create(
            first_name='Доктор',
            last_name='Врачев',
            middle_name='Владимирович',
            position='Терапевт',
            department='Поликлиника',
            email='doctor@example.com',
            phone='+7(903)456-78-90',
            status='active',
            user=self.user,
            hire_date=date.today()
        )

    def test_appointment_creation(self):
        """Тест создания записи на прием"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.staff,
            appointment_type='consultation',
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timezone.timedelta(hours=1),
            title='Консультация терапевта',
            description='Плановая консультация',
            status='scheduled'
        )
        
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.staff)
        self.assertEqual(appointment.appointment_type, 'consultation')
        self.assertEqual(appointment.status, 'scheduled')
        self.assertEqual(appointment.title, 'Консультация терапевта')


class ModelRelationshipTest(TestCase):
    def setUp(self):
        # Создаем связанного пациента
        self.patient = Patient.objects.create(
            first_name='Связанный',
            last_name='Пациент',
            date_of_birth=date(1990, 1, 1),
            gender='M'
        )

    def test_user_appointments_relationship(self):
        """Тест связи врача с записями на прием"""
        # Создаем врача
        doctor_user = User.objects.create_user(
            username='relation_doctor_unique',
            first_name='Доктор',
            last_name='Связанный'
        )
        
        # Создаем Staff для doctor поля
        doctor_staff = Staff.objects.create(
            first_name='Доктор',
            last_name='Связанный',
            middle_name='Владимирович',
            position='Терапевт',
            department='Поликлиника',
            email='doctor_relation@example.com',
            phone='+7(903)456-78-91',
            status='active',
            user=doctor_user,
            hire_date=date.today()
        )
        
        # Создаем запись на прием
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=doctor_staff,
            appointment_type='consultation',
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timezone.timedelta(hours=1),
            title='Консультация терапевта',
            description='Плановая консультация',
            status='scheduled'
        )
        
        # Проверяем связь
        doctor_appointments = Appointment.objects.filter(doctor=doctor_staff)
        self.assertIn(appointment, doctor_appointments)


class SystemSettingsModelTest(TestCase):
    def test_system_settings_creation(self):
        """Тест создания системных настроек"""
        settings = SystemSettings.objects.create(
            clinic_name='Тестовая клиника',
            timezone='Europe/Moscow',
            language='ru'
        )
        
        self.assertEqual(settings.clinic_name, 'Тестовая клиника')
        self.assertEqual(settings.timezone, 'Europe/Moscow')
        self.assertEqual(settings.language, 'ru')

    def test_system_settings_str_representation(self):
        """Тест строкового представления настроек"""
        settings = SystemSettings.objects.create(
            clinic_name='Тестовая клиника'
        )
        
        self.assertTrue(str(settings))  # Просто проверяем что str не пустой


class PatientDocumentModelTest(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            first_name='Документ',
            last_name='Пациент',
            date_of_birth=date(1980, 1, 1),
            gender='M',
            email='dokument.patsient@example.com',
            phone='+7(903)123-45-67',
            address='г. Москва, ул. Тверская, д. 1',
            passport_series='1234',
            passport_number='567890',
            insurance_policy='1234567890123456'
        )
    
    def test_patient_document_creation(self):
        """Тест создания документов пациента"""
        document = PatientDocument.objects.create(
            patient=self.patient,
            document_type='passport',
            description='Копия паспорта'
        )
        
        self.assertEqual(document.patient, self.patient)
        self.assertEqual(document.document_type, 'passport')
        self.assertEqual(document.description, 'Копия паспорта')


class MedicalRecordModelTest(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            first_name='Медицинский',
            last_name='Пациент',
            date_of_birth=date(1975, 1, 1),
            gender='M',
            email='meditsinskii.patsient@example.com',
            phone='+7(903)123-45-67',
            address='г. Москва, ул. Тверская, д. 1',
            passport_series='1234',
            passport_number='567890',
            insurance_policy='1234567890123456'
        )
        
        self.user = User.objects.create_user(
            username='medical_doctor',
            first_name='Медицинский',
            last_name='Доктор',
            email='medical.doctor@example.com'
        )

    def test_medical_record_creation(self):
        """Тест создания медицинской записи"""
        record = MedicalRecord.objects.create(
            patient=self.patient,
            record_type='diagnosis',
            content='Тестовый диагноз',
            created_by=self.user
        )
        
        self.assertEqual(record.patient, self.patient)
        self.assertEqual(record.record_type, 'diagnosis')
        self.assertEqual(record.content, 'Тестовый диагноз')
        self.assertEqual(record.created_by, self.user)
