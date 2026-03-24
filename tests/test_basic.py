"""Базовые тесты для проверки работоспособности."""
import numpy as np
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.math import Vec3
from core.field import Field


def test_vec3():
    """Тест Vec3."""
    v1 = Vec3(1, 2, 3)
    v2 = Vec3(4, 5, 6)
    
    assert (v1 + v2).x == 5
    assert (v1 - v2).x == -3
    assert (v1 * 2).x == 2
    assert v1.length() > 0
    
    print("✓ Vec3 тесты пройдены")


def test_field():
    """Тест поля."""
    cfg = {
        'noise': {
            'octaves': 4,
            'lacunarity': 2.0,
            'gain': 0.5,
            'sigma': 0.08,
            'warp_k1': 0.8,
            'warp_k2': 0.3,
            's1': 0.7,
            's2': 1.3
        },
        'grid': {
            'w_period': 8.0
        }
    }
    
    field = Field(cfg, seed=12345)
    value = field.sample(0, 0, 0, 0)
    
    assert isinstance(value, (float, np.floating))
    print(f"✓ Field тест пройден (значение: {value:.4f})")


if __name__ == "__main__":
    print("Запуск базовых тестов...")
    test_vec3()
    test_field()
    print("Все тесты пройдены!")

