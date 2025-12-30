import re
from typing import List, Tuple
from bs4 import BeautifulSoup
from tariff import Tariff
from config import Selectors
import logging

logger = logging.getLogger(__name__)

class TableParser:
    """Парсинг конкретных таблиц"""
    
    def __init__(self, extractor):
        self.extractor = extractor
    
    def parse_internet_table(self, table, section_name: str) -> List[Tariff]:
        """Парсинг таблицы интернет-тарифов"""
        tariffs = []
        
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 4:
                name = cells[0].text.strip()
                price = self.extractor.extract_number(cells[1].text)
                speed = self.extractor.extract_speed(cells[3].text)
                
                if name and price is not None:
                    tariffs.append(Tariff(
                        name=name,
                        price=price,
                        speed=speed
                    ))
        
        logger.info(f"Найдено интернет-тарифов {section_name}: {len(tariffs)}")
        return tariffs
    
    def parse_combo_table(self, table, section_name: str, suffix: str = '') -> List[Tariff]:
        """Парсинг комбо-тарифов"""
        tariffs = []
        
        # Извлекаем скорости из заголовков
        headers = table.find('thead').find_all('th')
        speeds = []
        for h in headers[1:]:
            match = re.search(r'(\d+)', h.text)
            speeds.append(float(match.group(1)) if match else None)
        
        # Парсим строки
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            if not cells:
                continue
            
            base_name = cells[0].text.strip()
            channels = self.extractor.extract_channels(base_name)
            clean_name = re.sub(r'\s*\(\d+\s*каналов?\)', '', base_name).strip()
            
            for i, speed in enumerate(speeds):
                if i < len(cells) - 1 and speed is not None:
                    price = self.extractor.extract_number(cells[i + 1].text)
                    if price is not None:
                        tariff_name = f"{clean_name} + {headers[i + 1].text.strip()}{suffix}"
                        tariffs.append(Tariff(
                            name=tariff_name,
                            channels=channels,
                            speed=speed,
                            price=price
                        ))
        
        logger.info(f"Найдено комбо-тарифов {section_name}: {len(tariffs)}")
        return tariffs