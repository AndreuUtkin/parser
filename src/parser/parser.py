import logging
from typing import List
from bs4 import BeautifulSoup

from config import Constants, Messages
from .html_fetcher import HtmlFetcher
from .data_extractor import DataExtractor
from .table_parser import TableParser
from .section_parser import SectionParser
from tariff import Tariff
from .tariff_processor import TariffProcessor

logger = logging.getLogger(__name__)

class RialcomParser:
    """Главный класс - координатор парсинга"""
    
    def __init__(self):
        # Внедрение зависимостей
        self.fetcher = HtmlFetcher()
        self.extractor = DataExtractor()
        self.table_parser = TableParser(self.extractor)
        self.section_parser = SectionParser(self.extractor, self.table_parser)
        self.processor = TariffProcessor()
    
    def parse_all(self) -> List[Tariff]:
        """Главный метод - координация всего процесса"""
        logger.info(Messages.PARSING_STARTED)
        
        # 1. Загрузка HTML
        soup = self.fetcher.fetch()
        
        # 2. Парсинг МКД
        mkd_tariffs = self.section_parser.parse_section(soup, 'collapse1', is_mkd=True)
        
        # 3. Создание маппинга каналов
        channels_map = self.section_parser.extract_mkd_channels_map(mkd_tariffs)
        
        # 4. Парсинг частных домов (с использованием каналов из МКД)
        private_tariffs = self.section_parser.parse_section(soup, 'collapse2', is_mkd=False)
        
        # 5. Объединение всех тарифов
        all_tariffs = mkd_tariffs + private_tariffs
        
        # 6. Валидация
        valid_tariffs, errors = self.processor.validate_tariffs(all_tariffs)
        
        # 7. Статистика
        stats = self.processor.get_statistics(valid_tariffs)
        
        logger.info(Messages.TARIFFS_FOUND.format(count=stats['total']))
        if errors:
            logger.warning(f"Найдено ошибок: {len(errors)}")
        
        return valid_tariffs