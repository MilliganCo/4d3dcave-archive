"""Коллектиблы."""
import numpy as np
from typing import List, Set
from core.math import Vec3
import time


class Pickup:
    """Один коллектибл."""
    
    def __init__(self, pos: Vec3, pickup_id: int):
        self.pos = pos
        self.id = pickup_id
        self.collected = False
        self.phase = np.random.uniform(0, 2 * np.pi)
        self.base_intensity = 1.0
        self.oscillation_amplitude = 0.3
        self.oscillation_freq = 2.0
    
    def get_intensity(self, t: float) -> float:
        """Интенсивность свечения в момент времени t."""
        if self.collected:
            return 0.0
        return self.base_intensity + self.oscillation_amplitude * np.sin(
            self.oscillation_freq * t + self.phase
        )
    
    def get_glow_data(self, t: float) -> tuple:
        """Данные для отрисовки свечения."""
        return (self.pos, self.get_intensity(t), 0.3)  # pos, intensity, size


class Pickups:
    """Менеджер коллектиблов."""
    
    def __init__(self, positions: List[Vec3]):
        self.pickups = [Pickup(pos, i) for i, pos in enumerate(positions)]
        self.collected_ids: Set[int] = set()
        self.start_time = time.time()
    
    def update(self, player_pos: Vec3, collect_radius: float = 1.5) -> int:
        """Обновление коллектиблов и проверка сбора."""
        collected_count = 0
        for pickup in self.pickups:
            if pickup.collected:
                continue
            
            dist = (pickup.pos - player_pos).length()
            if dist < collect_radius:
                pickup.collected = True
                self.collected_ids.add(pickup.id)
                collected_count += 1
        
        return collected_count
    
    def get_collected_count(self) -> int:
        """Количество собранных."""
        return len(self.collected_ids)
    
    def get_total_count(self) -> int:
        """Общее количество."""
        return len(self.pickups)
    
    def is_complete(self) -> bool:
        """Все ли собраны."""
        return len(self.collected_ids) == len(self.pickups)
    
    def get_glows(self) -> List[tuple]:
        """Получить данные для отрисовки свечений."""
        t = time.time() - self.start_time
        return [pickup.get_glow_data(t) for pickup in self.pickups if not pickup.collected]

