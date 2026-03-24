"""Физика и коллизии."""
import numpy as np
from typing import Tuple, Optional
from .math import Vec3


class Physics:
    """Система физики для игрока."""
    
    def __init__(self, cfg: dict):
        self.radius = cfg['player']['radius']
        self.height = cfg['player']['height']
        self.speed = cfg['player']['speed']
        self.jump_velocity = cfg['player']['jump']
        self.gravity = -9.81
        
        self.position = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.grounded = False
    
    def step(self, input_forward: Vec3, input_right: Vec3, 
             jump: bool, crouch: bool, dt: float,
             occupancy_mask: Optional[np.ndarray] = None,
             world_min: Optional[Vec3] = None,
             world_max: Optional[Vec3] = None) -> None:
        """Шаг физики."""
        # Движение (input_forward уже содержит комбинированное направление)
        move_dir = input_forward
        if move_dir.length() > 0:
            move_dir = move_dir.normalize()
        move_velocity = move_dir * self.speed
        
        # Приседание
        if crouch:
            move_velocity = move_velocity * 0.5
        
        # Применяем движение к скорости
        self.velocity.x = move_velocity.x
        self.velocity.z = move_velocity.z
        
        # Прыжок
        if jump and self.grounded:
            self.velocity.y = self.jump_velocity
        
        # Гравитация
        self.velocity.y += self.gravity * dt
        
        # Коллизии с простой геометрией (заглушка)
        # В полной версии здесь будет проверка с вокселями
        new_pos = self.position + self.velocity * dt
        
        # Простая проверка границ
        if world_min and world_max:
            new_pos.x = np.clip(new_pos.x, world_min.x + self.radius, world_max.x - self.radius)
            new_pos.z = np.clip(new_pos.z, world_min.z + self.radius, world_max.z - self.radius)
        
        # Проверка земли (простая заглушка)
        if new_pos.y < 0.5:  # Простой пол
            new_pos.y = 0.5
            self.velocity.y = 0.0
            self.grounded = True
        else:
            self.grounded = False
        
        self.position = new_pos
    
    def collide_capsule(self, pos: Vec3, vel: Vec3, 
                       occupancy_mask: Optional[np.ndarray] = None) -> Tuple[Vec3, bool]:
        """Коллизия капсулы с вокселями."""
        # Упрощенная версия: просто возвращаем позицию
        # В полной версии здесь будет проверка пересечения капсулы с вокселями
        return pos, True
    
    def raycast(self, origin: Vec3, direction: Vec3, max_dist: float) -> Optional[Vec3]:
        """Raycast для проверки видимости."""
        # Упрощенная версия
        return origin + direction * max_dist

