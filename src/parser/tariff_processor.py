from typing import List, Tuple
from tariff import Tariff
from config import Constants

class TariffProcessor:
    """Обработка и валидация собранных тарифов"""
    
    @staticmethod
    def validate_tariffs(tariffs: List[Tariff]) -> Tuple[List[Tariff], List[str]]:
        """Валидация тарифов и сбор ошибок"""
        valid_tariffs = []
        errors = []
        
        for tariff in tariffs:
            if not tariff.name:
                errors.append(f"Тариф без названия: {tariff}")
                continue
            if tariff.price is None:
                errors.append(f"Тариф без цены: {tariff.name}")
                continue
            valid_tariffs.append(tariff)
        
        return valid_tariffs, errors
    
    @staticmethod
    def get_statistics(tariffs: List[Tariff]) -> dict:
        """Сбор статистики по тарифам"""
        total = len(tariffs)
        expected = Constants.EXPECTED_TARIFFS
        
        stats = {
            'total': total,
            'expected': expected,
            'difference': total - expected,
            'percentage': round((total / expected * 100), 1) if expected > 0 else 0
        }
        
        return stats