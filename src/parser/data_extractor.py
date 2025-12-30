import re
from typing import Optional

class DataExtractor:
    """Извлечение данных из текста (скорость, цена, каналы)"""
    
    @staticmethod
    def extract_number(text: str) -> Optional[float]:
        if not text:
            return None
        text = text.replace(' ', '').replace(',', '.')
        match = re.search(r'(\d+\.?\d*)', text)
        return float(match.group(1)) if match else None
    
    @staticmethod
    def extract_speed(text: str) -> Optional[float]:
        if not text:
            return None
        if text.startswith('до '):
            text = text[3:]
        
        is_kbps = any(unit in text.lower() for unit in ['кбит', 'kbit', 'кб/с'])
        speed = DataExtractor.extract_number(text)
        
        if speed:
            return round(speed / 1000, 1) if is_kbps else speed
        return None
    
    @staticmethod
    def extract_channels(text: str) -> Optional[int]:
        if not text:
            return None
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