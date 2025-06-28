# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from core.models import Patient, Doctor, Service, Appointment


class PatientViewsTest(TestCase):
    """Тесты для представлений пациентов"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.client = Client()
        
        # Создаем пользователя и врача для аутентификации
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Тест',
            last_name='Пользователь'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.user,
            specialization='Терапевт'
        )
        
        # Создаем тестового пациента
        self.patient = Patient.objects.create(
            first_name='Тест',
            last_name='Пациент',
            patronymic='Тестович',
            date_of_birth=date(1990, 1, 1),
            gender='M',
            phone='+7 (999) 123-45-67',
            email='patient@test.com'
        )
    
    def test_patient_list_view_requires_login(self):
        """Тест: список пациентов требует аутентификации"""
        response = self.client.get(reverse('core:patient_list'))
        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)
    
    def test_patient_list_view_authenticated(self):
        """Тест: список пациентов для аутентифицированного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:patient_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пациент Тест')
        self.assertIn('patients', response.context)
    
    def test_patient_detail_view(self):
        """Тест: детальная страница пациента"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('core:patient_detail', kwargs={'pk': self.patient.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient'], self.patient)
        self.assertContains(response, 'Пациент Тест Тестович')
    
    def test_patient_create_view_get(self):
        """Тест: GET запрос на создание пациента"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:patient_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
    
    def test_patient_create_view_post_valid(self):
        """Тест: POST запрос с валидными данными для создания пациента"""
        self.client.login(username='testuser', password='testpass123')
        
        patient_data = {
            'first_name': 'Новый',
            'last_name': 'Пациент',
            'patronymic': 'Тестович',
            'date_of_birth': '1985-12-25',
            'gender': 'F',
            'phone': '+7 (999) 987-65-43',
            'email': 'new_patient@test.com'
        }
        
        response = self.client.post(reverse('core:patient_create'), patient_data)
        
        # Должен быть редирект после успешного создания
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что пациент создан
        self.assertTrue(
            Patient.objects.filter(
                first_name='Новый',
                last_name='Пациент'
            ).exists()
        )
    
    def test_patient_create_view_post_invalid(self):
        """Тест: POST запрос с невалидными данными"""
        self.client.login(username='testuser', password='testpass123')
        
        # Данные без обязательных полей
        invalid_data = {
            'first_name': '',  # Пустое имя
            'last_name': 'Пациент',
            'gender': 'M'
        }
        
        response = self.client.post(reverse('core:patient_create'), invalid_data)
        
        # Должна отобразиться форма с ошибками
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'first_name', 'Это поле обязательно для заполнения.')


class AppointmentViewsTest(TestCase):
    """Тесты для представлений записей на прием"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.client = Client()
        
        # Создаем пользователей и врачей
        self.user = User.objects.create_user(
            username='testdoctor',
            password='testpass123'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.user,
            specialization='Кардиолог'
        )
        
        # Создаем пациента
        self.patient = Patient.objects.create(
            first_name='Тест',
            last_name='Пациент',
            date_of_birth=date(1980, 6, 15),
            gender='M'
        )
        
        # Создаем услугу
        self.service = Service.objects.create(
            name='Консультация кардиолога',
            price=Decimal('2500.00'),
            duration_minutes=45
        )
        
        # Создаем запись на прием
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_time=timezone.now() + timedelta(days=1),
            status='scheduled'
        )
    
    def test_appointment_list_view_requires_login(self):
        """Тест: список записей требует аутентификации"""
        response = self.client.get(reverse('core:appointment_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_appointment_list_view_authenticated(self):
        """Тест: список записей для аутентифицированного пользователя"""
        self.client.login(username='testdoctor', password='testpass123')
        response = self.client.get(reverse('core:appointment_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('appointments', response.context)
        self.assertContains(response, 'Консультация кардиолога')
    
    def test_appointment_detail_view(self):
        """Тест: детальная страница записи"""
        self.client.login(username='testdoctor', password='testpass123')
        response = self.client.get(
            reverse('core:appointment_detail', kwargs={'pk': self.appointment.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['appointment'], self.appointment)
    
    def test_appointment_create_view_get(self):
        """Тест: GET запрос на создание записи"""
        self.client.login(username='testdoctor', password='testpass123')
        response = self.client.get(reverse('core:appointment_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
    
    def test_appointment_create_view_post_valid(self):
        """Тест: POST запрос с валидными данными для создания записи"""
        self.client.login(username='testdoctor', password='testpass123')
        
        future_time = timezone.now() + timedelta(days=2)
        appointment_data = {
            'patient': self.patient.pk,
            'doctor': self.doctor.pk,
            'service': self.service.pk,
            'appointment_time': future_time.strftime('%Y-%m-%d %H:%M'),
            'status': 'scheduled'
        }
        
        response = self.client.post(reverse('core:appointment_create'), appointment_data)
        
        # Должен быть редирект после успешного создания
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что запись создана
        self.assertEqual(Appointment.objects.count(), 2)  # Было 1 + 1 новая


class DashboardViewsTest(TestCase):
    """Тесты для представлений панели управления"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='admin_user',
            password='adminpass123',
            is_staff=True
        )
        
        self.doctor = Doctor.objects.create(
            user=self.user,
            specialization='Главный врач'
        )
        
        # Создаем некоторые данные для статистики
        patient = Patient.objects.create(
            first_name='Статистика',
            last_name='Пациент',
            date_of_birth=date(1995, 3, 10),
            gender='F'
        )
        
        service = Service.objects.create(
            name='Статистическая услуга',
            price=Decimal('1000.00')
        )
        
        Appointment.objects.create(
            patient=patient,
            doctor=self.doctor,
            service=service,
            appointment_time=timezone.now() + timedelta(hours=2),
            status='scheduled'
        )
    
    def test_dashboard_view_requires_login(self):
        """Тест: панель управления требует аутентификации"""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_view_authenticated(self):
        """Тест: панель управления для аутентифицированного пользователя"""
        self.client.login(username='admin_user', password='adminpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что контекст содержит статистические данные
        context = response.context
        self.assertIn('total_patients', context)
        self.assertIn('total_appointments', context)
        self.assertIn('total_doctors', context)
        
        # Проверяем значения статистики
        self.assertEqual(context['total_patients'], 1)
        self.assertEqual(context['total_appointments'], 1)
        self.assertEqual(context['total_doctors'], 1)


class SearchAndFilterTest(TestCase):
    """Тесты для поиска и фильтрации"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='search_user',
            password='searchpass123'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.user,
            specialization='Терапевт'
        )
        
        # Создаем несколько пациентов для поиска
        self.patient1 = Patient.objects.create(
            first_name='Анна',
            last_name='Иванова',
            date_of_birth=date(1985, 1, 1),
            gender='F'
        )
        
        self.patient2 = Patient.objects.create(
            first_name='Петр',
            last_name='Петров',
            date_of_birth=date(1990, 5, 15),
            gender='M'
        )
        
        self.patient3 = Patient.objects.create(
            first_name='Анна',
            last_name='Сидорова',
            date_of_birth=date(1995, 12, 20),
            gender='F'
        )
    
    def test_patient_search_by_name(self):
        """Тест: поиск пациентов по имени"""
        self.client.login(username='search_user', password='searchpass123')
        
        response = self.client.get(reverse('core:patient_list'), {'search': 'Анна'})
        
        self.assertEqual(response.status_code, 200)
        
        # Должны найтись оба пациента с именем "Анна"
        patients = response.context['patients']
        self.assertEqual(len(patients), 2)
        
        # Проверяем, что найдены правильные пациенты
        patient_names = [p.first_name for p in patients]
        self.assertIn('Анна', patient_names)
    
    def test_patient_search_by_last_name(self):
        """Тест: поиск пациентов по фамилии"""
        self.client.login(username='search_user', password='searchpass123')
        
        response = self.client.get(reverse('core:patient_list'), {'search': 'Петров'})
        
        self.assertEqual(response.status_code, 200)
        
        patients = response.context['patients']
        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0].last_name, 'Петров')
    
    def test_patient_filter_by_gender(self):
        """Тест: фильтрация пациентов по полу"""
        self.client.login(username='search_user', password='searchpass123')
        
        response = self.client.get(reverse('core:patient_list'), {'gender': 'F'})
        
        self.assertEqual(response.status_code, 200)
        
        patients = response.context['patients']
        # Должны найтись 2 женщины
        self.assertEqual(len(patients), 2)
        
        # Все найденные пациенты должны быть женского пола
        for patient in patients:
            self.assertEqual(patient.gender, 'F')
