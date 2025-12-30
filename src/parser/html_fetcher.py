import requests
from bs4 import BeautifulSoup
import logging
from config import Constants

logger = logging.getLogger(__name__)

class HtmlFetcher:
    """Отвечает только за загрузку HTML"""
    
    def __init__(self, base_url: str = Constants.BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def fetch(self) -> BeautifulSoup:
        logger.info(f"Загрузка: {self.base_url}")
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            logger.info("Страница загружена")
            return BeautifulSoup(response.text, 'lxml')
        except requests.RequestException as e:
            logger.error(f"Ошибка загрузки: {e}")
            raise