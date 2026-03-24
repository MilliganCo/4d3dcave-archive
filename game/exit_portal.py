"""Выходной портал."""
import numpy as np
from core.math import Vec3


class ExitPortal:
    """Выходной портал."""
    
    def __init__(self, pos: Vec3):
        self.pos = pos
        self.active = False
        self.size = 2.0
    
    def activate(self):
        """Активация портала."""
        self.active = True
    
    def check_intersection(self, player_pos: Vec3, radius: float = 0.5) -> bool:
        """Проверка пересечения с игроком."""
        if not self.active:
            return False
        
        dist = (self.pos - player_pos).length()
        return dist < (self.size + radius)
    
    def get_glow_data(self) -> tuple:
        """Данные для отрисовки."""
        intensity = 1.5 if self.active else 0.3
        return (self.pos, intensity, self.size)

