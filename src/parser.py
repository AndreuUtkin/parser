import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Optional
from urllib.parse import urljoin
from .tariff import Tariff

logger = logging.getLogger(__name__)

# Парсер тарифов
class Parser:
    def __init__(self, base_url: str = "https://www.rialcom.ru/internet_tariffs/"):
        self.base_url = base_url
        self.session = requests.Session()
        self._setup_session()
        
    # Настройка HTTP сессии
    def _setup_session(self):
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    # Загрузка HTML страницы
    def fetch_page(self) -> BeautifulSoup:
        
        logger.info(f"Загрузка страницы: {self.base_url}")
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            # Проверка кодировки
            response.encoding = response.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            logger.info("Страница успешно загружена")
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Ошибка : {e}")
            raise
    #Извлечение числа
    def _extract_number(self, text: str) -> Optional[float]:
        
        if not text:
            return None
        
        # Удаляем пробелы и заменяем запятые на точки
        text = text.replace(' ', '').replace(',', '.')
        
        # Ищем число 
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
    
    #Извлечение скорости с конвертацией кбит/с в мбит/с
    def _extract_speed(self, text: str) -> Optional[float]:
        
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Убираем до если есть
        if text.startswith('до '):
            text = text[3:]
        
        # Определяем единицы измерения
        is_kbps = any(unit in text_lower for unit in ['кбит', 'kbit', 'кб/с'])
        
        # Извлекаем число
        speed = self._extract_number(text)
        
        if speed:
            # Конвертируем кбит/с в Мбит/с
            if is_kbps:
                return round(speed / 1000, 1)
            return speed
        
        return None
    
    #Извлечение количества каналов
    def _extract_channels(self, text: str) -> Optional[int]:
       
        if not text:
            return None
        
        # Паттерны: (165 каналов) или 165 каналов
        patterns = [
            r'\((\d+)\s*каналов?\)',
            r'(\d+)\s*каналов?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    # Парсинг тарифов для МКД   
    def parse_mkd_internet(self, soup: BeautifulSoup) -> List[Tariff]:
    
        tariffs = []
        logger.info("Парсинг МКД интернет-тарифов...")
        
        try:
            # Находим секцию МКД
            mkd_section = soup.find('div', id='collapse1')
            if not mkd_section:
                logger.warning("Секция МКД не найдена")
                return tariffs
            
            # Ищем заголовок "Интернет" и следующую таблицу
            internet_header = mkd_section.find('div', class_='bg-danger')
            if not internet_header or 'интернет' not in internet_header.text.lower():
                logger.warning("Заголовок интернет-тарифов МКД не найден")
                return tariffs
            
            table = internet_header.find_next('table')
            if not table:
                logger.warning("Таблица интернет-тарифов МКД не найдена")
                return tariffs
            
            # Парсим строки таблицы
            rows = table.find('tbody').find_all('tr')
            logger.info(f"Найдено {len(rows)} интернет-тарифов МКД")
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    name = cells[0].text.strip()
                    price_text = cells[1].text.strip()
                    speed_text = cells[3].text.strip()
                    
                    # Извлекаем данные
                    price = self._extract_number(price_text)
                    speed = self._extract_speed(speed_text)
                    
                    if name and price is not None:
                        tariff = Tariff(
                            name=name,
                            price=price,
                            speed=speed
                        )
                        tariffs.append(tariff)
                        logger.debug(f"Добавлен МКД интернет-тариф: {name}")
            
            return tariffs
            
        except Exception as e:
            logger.error(f"Ошибка парсинга МКД интернет-тарифов: {e}")
            return tariffs
    
    #Парсинг комбо-тарифов (Интернет+ТВ) для МКД
    def parse_mkd_combo(self, soup: BeautifulSoup) -> List[Tariff]:
        
        tariffs = []
        logger.info("Парсинг МКД комбо-тарифов...")
        
        try:
            mkd_section = soup.find('div', id='collapse1')
            if not mkd_section:
                return tariffs
            
            # Ищем заголовок комбо-тарифов
            combo_header = mkd_section.find('div', class_='bg-dark')
            if not combo_header or 'интернет + интерактивное тв' not in combo_header.text.lower():
                return tariffs
            
            table = combo_header.find_next('table')
            if not table:
                return tariffs
            
            # Извлекаем скорости из заголовков
            headers = table.find('thead').find_all('th')
            speeds = []
            column_names = []
            
            for header in headers[1:]:  # Пропускаем заголовок
                header_text = header.text.strip()
                column_names.append(header_text)
                
                # Извлекаем скорость из названия столбца
                speed_match = re.search(r'(\d+)', header_text)
                if speed_match:
                    speeds.append(float(speed_match.group(1)))
                else:
                    speeds.append(None)
            
            # Парсим строки
            rows = table.find('tbody').find_all('tr')
            logger.info(f"Найдено {len(rows)} комбо-тарифов МКД")
            
            for row in rows:
                cells = row.find_all('td')
                if not cells:
                    continue
                
                base_name = cells[0].text.strip()
                channels = self._extract_channels(base_name)
                
                # Очищаем базовое название от информации о каналах
                clean_name = re.sub(r'\s*\(\d+\s*каналов?\)', '', base_name).strip()
                
                # Создаем тариф для каждого столбца
                for i, (speed, col_name) in enumerate(zip(speeds, column_names)):
                    if i < len(cells) - 1 and speed is not None:
                        price_text = cells[i + 1].text.strip()
                        price = self._extract_number(price_text)
                        
                        if price is not None:
                            # Формируем полное название
                            tariff_name = f"{clean_name} + {col_name}"
                            
                            tariff = Tariff(
                                name=tariff_name,
                                channels=channels,
                                speed=speed,
                                price=price
                            )
                            tariffs.append(tariff)
                            logger.debug(f"Добавлен МКД комбо-тариф: {tariff_name}")
            
            return tariffs
            
        except Exception as e:
            logger.error(f"Ошибка парсинга МКД комбо: {e}")
            return tariffs
    
    #Парсинг тарифов для частных домов
    def parse_private_internet(self, soup: BeautifulSoup) -> List[Tariff]:
        
        tariffs = []
        logger.info("Парсинг частных тарифов...")
        
        try:
            private_section = soup.find('div', id='collapse2')
            if not private_section:
                return tariffs
            
            internet_header = private_section.find('div', class_='bg-danger')
            if not internet_header or 'интернет' not in internet_header.text.lower():
                return tariffs
            
            table = internet_header.find_next('table')
            if not table:
                return tariffs
            
            rows = table.find('tbody').find_all('tr')
            logger.info(f"Найдено {len(rows)} интернет-тарифов частных домов")
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    name = cells[0].text.strip()
                    price_text = cells[1].text.strip()
                    speed_text = cells[3].text.strip()
                    
                    price = self._extract_number(price_text)
                    speed = self._extract_speed(speed_text)
                    
                    if name and price is not None:
                        tariff = Tariff(
                            name=name,
                            price=price,
                            speed=speed
                        )
                        tariffs.append(tariff)
            
            return tariffs
            
        except Exception as e:
            logger.error(f"Ошибка парсинга частных тарифов: {e}")
            return tariffs
    
    #Парсинг комбо-тарифов для частных домов
    def parse_private_combo(self, soup: BeautifulSoup, mkd_channels_map: dict) -> List[Tariff]:
        
        tariffs = []
        logger.info("Парсинг частных комбо-тарифов...")
        
        try:
            private_section = soup.find('div', id='collapse2')
            if not private_section:
                return tariffs
            
            combo_header = private_section.find('div', class_='bg-dark')
            if not combo_header or 'интернет + интерактивное тв' not in combo_header.text.lower():
                return tariffs
            
            table = combo_header.find_next('table')
            if not table:
                return tariffs
            
            # Извлекаем скорости из заголовков
            headers = table.find('thead').find_all('th')
            speeds = []
            column_names = []
            
            for header in headers[1:]:  # Пропускаем первый столбец
                header_text = header.text.strip()
                column_names.append(header_text)
                
                speed_match = re.search(r'(\d+)', header_text)
                if speed_match:
                    speeds.append(float(speed_match.group(1)))
                else:
                    speeds.append(None)
            
            rows = table.find('tbody').find_all('tr')
            logger.info(f"Найдено {len(rows)} комбо-тарифов частных домов")
            
            for row in rows:
                cells = row.find_all('td')
                if not cells:
                    continue
                
                base_name = cells[0].text.strip()
                
                # Берем количество каналов из МКД 
                clean_base_name = re.sub(r'\s*\(\d+\s*каналов?\)', '', base_name).strip()
                channels = mkd_channels_map.get(clean_base_name)
                
                # Создаем тариф для каждого столбца
                for i, (speed, col_name) in enumerate(zip(speeds, column_names)):
                    if i < len(cells) - 1 and speed is not None:
                        price_text = cells[i + 1].text.strip()
                        price = self._extract_number(price_text)
                        
                        if price is not None:
                            
                            tariff_name = f"{clean_base_name} + {col_name}_ч"
                            
                            tariff = Tariff(
                                name=tariff_name,
                                channels=channels,
                                speed=speed,
                                price=price
                            )
                            tariffs.append(tariff)
            
            return tariffs
            
        except Exception as e:
            logger.error(f"Ошибка парсинга частных комбо-тарифов: {e}")
            return tariffs
    
    # Парсинг всех тарифов
    def parse_all(self) -> List[Tariff]:
        logger.info("Начало парсинга тарифов...")
        
        # Загружаем страницу
        soup = self.fetch_page()
        
        all_tariffs = []
        
        # Парсим МКД интернет-тарифы
        mkd_internet = self.parse_mkd_internet(soup)
        all_tariffs.extend(mkd_internet)
        
        # Парсим МКД комбо-тарифы
        mkd_combo = self.parse_mkd_combo(soup)
        all_tariffs.extend(mkd_combo)
        
        # Создаем маппинг названий
        mkd_channels_map = {}
        for tariff in mkd_combo:
            # Извлекаем базовое название без части про скорость
            base_name_parts = tariff.name.split(' + РиалКом Интернет')[0].strip()
            mkd_channels_map[base_name_parts] = tariff.channels
        
        # Парсим частные интернет-тарифы
        private_internet = self.parse_private_internet(soup)
        all_tariffs.extend(private_internet)
        
        # Парсим частные комбо-тарифы
        private_combo = self.parse_private_combo(soup, mkd_channels_map)
        all_tariffs.extend(private_combo)
        
        return all_tariffs