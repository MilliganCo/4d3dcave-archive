"""Генерация стартовой точки и размещение коллектиблов."""
import numpy as np
from typing import List, Tuple, Optional
from numba import njit
from .field import Field
from .math import Vec3


# Убрали njit для этой функции, так как она использует Python объекты


def find_start_point(field: Field, cfg: dict, rng: np.random.Generator) -> Vec3:
    """Поиск стартовой точки для игрока."""
    region_size = cfg['grid']['region_size']
    cell_size = cfg['grid']['cell_size']
    iso = cfg['grid']['iso']
    safe_radius = cfg['gameplay']['start_safe_radius']
    w = 0.0  # Стартовая w
    
    # Сэмплируем несколько точек
    best_point = None
    best_score = -1.0
    
    for _ in range(100):
        x = rng.uniform(-region_size * cell_size * 0.3, region_size * cell_size * 0.3)
        y = rng.uniform(1.0, 5.0)
        z = rng.uniform(-region_size * cell_size * 0.3, region_size * cell_size * 0.3)
        
        # Проверяем, что точка в полости
        value = field.sample(x, y, z, w)
        if value >= iso:
            continue
        
        # Оценка "просторности" (упрощенная)
        score = 0.0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    v = field.sample(x + dx * safe_radius, y + dy * safe_radius, 
                                   z + dz * safe_radius, w)
                    if v < iso:
                        score += 1.0
        
        if score > best_score:
            best_score = score
            best_point = Vec3(x, y, z)
    
    if best_point is None:
        # Fallback: центр
        return Vec3(0, 2, 0)
    
    return best_point


def poisson_disk_sample(field: Field, cfg: dict, n: int, 
                       center: Vec3, rng: np.random.Generator) -> List[Vec3]:
    """Poisson disk sampling для размещения коллектиблов."""
    min_dist = cfg['gameplay']['pickup_spacing']
    wall_dist = cfg['gameplay']['wall_distance']
    iso = cfg['grid']['iso']
    w = 0.0
    
    points: List[Vec3] = []
    
    # Область поиска
    region_size = cfg['grid']['region_size'] * cfg['grid']['cell_size'] * 0.5
    
    max_attempts = n * 100
    attempts = 0
    
    while len(points) < n and attempts < max_attempts:
        attempts += 1
        
        # Генерируем случайную точку
        x = rng.uniform(center.x - region_size, center.x + region_size)
        y = rng.uniform(center.y - 5, center.y + 10)
        z = rng.uniform(center.z - region_size, center.z + region_size)
        
        candidate = Vec3(x, y, z)
        
        # Проверяем, что точка в полости
        value = field.sample(x, y, z, w)
        if value >= iso:
            continue
        
        # Проверяем расстояние до стен
        wall_check_ok = True
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    check_pos = Vec3(x + dx * wall_dist, y + dy * wall_dist, z + dz * wall_dist)
                    v = field.sample(check_pos.x, check_pos.y, check_pos.z, w)
                    if v >= iso:
                        wall_check_ok = False
                        break
                if not wall_check_ok:
                    break
            if not wall_check_ok:
                break
        
        if not wall_check_ok:
            continue
        
        # Проверяем расстояние до других точек
        too_close = False
        for existing in points:
            dist = (candidate - existing).length()
            if dist < min_dist:
                too_close = True
                break
        
        if not too_close:
            points.append(candidate)
    
    return points

