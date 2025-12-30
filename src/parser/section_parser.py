from typing import List, Dict
from bs4 import BeautifulSoup
from tariff import Tariff
from config import Selectors
from .table_parser import TableParser
import logging

logger = logging.getLogger(__name__)

class SectionParser:
    """Парсинг конкретной секции сайта (МКД или частные дома)"""
    
    def __init__(self, extractor, table_parser):
        self.extractor = extractor
        self.table_parser = table_parser
    
    def parse_section(self, soup: BeautifulSoup, section_id: str, is_mkd: bool = True) -> List[Tariff]:
        """Парсит всю секцию (интернет + комбо)"""
        section = soup.find('div', id=section_id)
        if not section:
            logger.warning(f"Секция {section_id} не найдена")
            return []
        
        tariffs = []
        
        # Интернет-тарифы
        internet_table = Selectors.get_internet_table(section)
        if internet_table:
            section_name = "МКД" if is_mkd else "частные"
            internet_tariffs = self.table_parser.parse_internet_table(internet_table, section_name)
            tariffs.extend(internet_tariffs)
        
        # Комбо-тарифы
        combo_table = Selectors.get_combo_table(section)
        if combo_table:
            suffix = '' if is_mkd else '_ч'
            combo_tariffs = self.table_parser.parse_combo_table(combo_table, section_name, suffix)
            tariffs.extend(combo_tariffs)
        
        return tariffs
    
    def extract_mkd_channels_map(self, mkd_tariffs: List[Tariff]) -> Dict[str, int]:
        """Создает маппинг названий -> количество каналов для МКД"""
        channels_map = {}
        for tariff in mkd_tariffs:
            if tariff.channels:
                # Извлекаем базовое название без части про скорость
                base_name = tariff.name.split(' + РиалКом Интернет')[0].strip()
                channels_map[base_name] = tariff.channels
        return channels_map