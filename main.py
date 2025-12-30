#!/usr/bin/env python3
import sys
import logging
from parser.parser import RialcomParser
from excel_exporter import ExcelExporter
from config import Constants, Messages

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def print_statistics(tariffs):
    """Красивая статистика"""
    from parser.tariff_processor import TariffProcessor
    stats = TariffProcessor.get_statistics(tariffs)
    
    print("\n" + "="*50)
    print("СТАТИСТИКА ПАРСИНГА")
    print("="*50)
    print(f"Всего тарифов: {stats['total']}")
    print(f"Ожидалось: {stats['expected']}")
    print(f"Разница: {stats['difference']} ({stats['percentage']}%)")
    print("="*50)

def main():
    try:
        # Создаем парсер
        parser = RialcomParser()
        
        # Парсим
        tariffs = parser.parse_all()
        
        if not tariffs:
            print("❌ Тарифы не найдены!")
            return 1
        
        # Статистика
        print_statistics(tariffs)
        
        # Экспорт
        exporter = ExcelExporter(Constants.OUTPUT_FILENAME)
        exporter.export_to_excel(tariffs)
        
        print(f"\n✅ Файл сохранен: {Constants.OUTPUT_FILENAME}")
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Остановлено пользователем")
        return 130
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())