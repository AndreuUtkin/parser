class Selectors:
    """CSS селекторы для парсинга"""
    MKD_SECTION = 'div#collapse1'
    PRIVATE_SECTION = 'div#collapse2'
    INTERNET_HEADER = 'div.bg-danger'
    COMBO_HEADER = 'div.bg-dark'
    INTERNET_TABLE = 'div.bg-danger + table'
    COMBO_TABLE = 'div.bg-dark + table'
    
    @classmethod
    def get_internet_table(cls, section):
        return section.find('div', class_='bg-danger').find_next('table')
    
    @classmethod
    def get_combo_table(cls, section):
        return section.find('div', class_='bg-dark').find_next('table')

class Constants:
    EXPECTED_TARIFFS = 106
    OUTPUT_FILENAME = 'rialcom_tariffs.xlsx'
    BASE_URL = 'https://www.rialcom.ru/internet_tariffs/'
    
class Messages:
    PAGE_LOADED = 'Страница загружена'
    PARSING_STARTED = 'Начало парсинга...'
    TARIFFS_FOUND = 'Найдено тарифов: {count}'