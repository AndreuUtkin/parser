from dataclasses import dataclass
from typing import Optional
import re
#Модель тарифа
@dataclass
class Tariff:
    name: str
    channels: Optional[int] = None
    speed: Optional[float] = None  # Мбит/с
    price: Optional[float] = None
    
    
    # Очистка данных
    def __post_init__(self):
        
        if self.name:
            self.name = re.sub(r'\s+', ' ', self.name).strip()
            
        if self.speed and self.speed > 1000:
            self.speed = round(self.speed / 1000, 1)
            
    # каналы для excel
    @property
    def excel_channels(self):
        
        return self.channels if self.channels is not None else "null"
    
    # скорость для excel
    @property
    def excel_speed(self):
        return self.speed if self.speed is not None else "null"
    
    # словарь для excel
    def to_dict(self):
        return {
            "Название тарифа": self.name,
            "Количество каналов": self.excel_channels,
            "Скорость доступа": self.excel_speed,
            "Абонентская плата": self.price
        }