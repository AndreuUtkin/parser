import sys
import logging
from typing import List
from src.parser import Parser
from src.excel_exporter import ExcelExporter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('parser.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def main():
    
    try:
        
        parser = Parser()
        
        print("\n Сбор тарифов ...")
        tariffs = parser.parse_all()
        
        if not tariffs:
            print("\n Нет тарифов")
            sys.exit(1)
        else:
            print(f"\n Успех! Собрано {len(tariffs)} тарифов")
        
        print("\n Экспортируем в Excel...")
        exporter = ExcelExporter("tariffs.xlsx")
        exporter.export_to_excel(tariffs)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n Остановка")
        return 130
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())