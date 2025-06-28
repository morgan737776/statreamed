import time
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction
from medical_history.models import ICD10Disease as ICD10Code

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

BASE_URL = 'https://mkb-10.com'

class Command(BaseCommand):
    help = 'Импортирует справочник МКБ-10 с сайта mkb-10.com используя Selenium'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    def get_soup(self, url):
        try:
            self.driver.get(url)
            time.sleep(3) # Ожидание для JS
            html = self.driver.page_source
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при загрузке страницы {url} через Selenium: {e}'))
            return None

    def handle(self, *args, **options):
        self.stdout.write('Начало импорта справочника МКБ-10...')
        self.stdout.write('Очистка старых данных...')
        ICD10Code.objects.all().delete()

        try:
            self.import_classes()
            self.stdout.write(self.style.SUCCESS('Импорт МКБ-10 успешно завершен!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Произошла критическая ошибка: {e}'))
        finally:
            self.driver.quit()
            self.stdout.write('Драйвер Selenium закрыт.')

    @transaction.atomic
    def import_classes(self):
        soup = self.get_soup(BASE_URL)
        if not soup:
            self.stderr.write(self.style.ERROR('Не удалось получить главную страницу. Прерывание.'))
            return

        # Находим все параграфы в основном контенте
        main_content = soup.find('main', {'id': 'cnt'})
        if not main_content:
            self.stderr.write(self.style.ERROR('Не удалось найти основной контент на странице.'))
            return

        paragraphs = main_content.find_all('p', recursive=False)
        
        i = 0
        while i < len(paragraphs):
            p_name = paragraphs[i]
            # Проверяем, есть ли следующий параграф для кода
            if i + 1 >= len(paragraphs):
                i += 1
                continue

            p_code = paragraphs[i+1]

            link = p_name.find('a', href=lambda href: href and 'pid=' in href)
            code_tag = p_code.find('b')

            if link and code_tag:
                class_name = link.get_text(strip=True)
                class_url = BASE_URL + link['href']
                code = code_tag.get_text(strip=True)

                class_db_item, created = ICD10Code.objects.get_or_create(
                    code=code,
                    defaults={'name': class_name, 'is_category': True}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Класс: {code} - {class_name}'))
                
                self.import_blocks(class_url, class_db_item)
                i += 2 # Переходим к следующей паре параграфов
            else:
                i += 1 # Двигаемся дальше, если пара не найдена

    def import_blocks(self, class_url, parent_class):
        soup = self.get_soup(class_url)
        if not soup:
            return

        # На страницах классов и блоков структура одинаковая
        for item in soup.select('main#cnt .block_list li a, main#cnt p a[href*="pid="]'):
            item_text = item.get_text(strip=True)
            item_url = BASE_URL + item['href']
            
            try:
                code, name = item_text.split(' ', 1)
            except ValueError:
                code = item_text
                name = ''

            # Проверяем, является ли код диапазоном (блок) или конкретным кодом
            is_category = '-' in code or not any(char.isdigit() for char in code.replace('.', ''))

            db_item, created = ICD10Code.objects.get_or_create(
                code=code,
                defaults={'name': name, 'parent': parent_class, 'is_category': is_category}
            )
            if created:
                self.stdout.write(f'  -> {code} - {name}')

            # Если это категория (блок), рекурсивно импортируем его содержимое
            if is_category:
                self.import_codes(item_url, db_item)

    def import_codes(self, block_url, parent_block):
        soup = self.get_soup(block_url)
        if not soup:
            return

        for item in soup.select('main#cnt .block_list li a, main#cnt p a[href*="pid="]'):
            item_text = item.get_text(strip=True)
            
            try:
                code, name = item_text.split(' ', 1)
            except ValueError:
                code = item_text
                name = ''

            code_db_item, created = ICD10Code.objects.get_or_create(
                code=code.strip(),
                defaults={'name': name.strip(), 'parent': parent_block, 'is_category': False}
            )
            if created:
                self.stdout.write(f'    -->> {code} - {name}')
