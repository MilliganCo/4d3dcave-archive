"""4D скалярное поле с периодизацией по w."""
import numpy as np
from numba import njit
from typing import Tuple
from .noise4d import fbm_4d, domain_warp_4d


@njit
def sample_field(x: float, y: float, z: float, w: float,
                 octaves: int, lacunarity: float, gain: float,
                 sigma: float, warp_k1: float, warp_k2: float,
                 s1: float, s2: float, w_period: float, seed: int) -> float:
    """Сэмплирование 4D поля с периодизацией w."""
    # Периодизация w
    u = np.cos(2.0 * np.pi * w / w_period)
    v = np.sin(2.0 * np.pi * w / w_period)
    w_periodic = 0.5 * u + 0.5 * v  # Преобразуем в диапазон [0, 1]
    
    # Domain warping
    rx, ry, rz, rw = domain_warp_4d(
        x, y, z, w_periodic,
        warp_k1, warp_k2, s1, s2,
        octaves, lacunarity, gain, sigma, seed
    )
    
    # Основной шум
    value = fbm_4d(rx, ry, rz, rw, octaves, lacunarity, gain, sigma, seed)
    
    # Bias для получения большего количества полостей
    bias = 0.2
    return value - bias


@njit
def field_gradient(x: float, y: float, z: float, w: float,
                   octaves: int, lacunarity: float, gain: float,
                   sigma: float, warp_k1: float, warp_k2: float,
                   s1: float, s2: float, w_period: float, seed: int,
                   eps: float = 0.01) -> Tuple[float, float, float]:
    """Градиент поля (центральные разности по x, y, z)."""
    fx = sample_field(x + eps, y, z, w, octaves, lacunarity, gain, sigma,
                      warp_k1, warp_k2, s1, s2, w_period, seed)
    fx_neg = sample_field(x - eps, y, z, w, octaves, lacunarity, gain, sigma,
                          warp_k1, warp_k2, s1, s2, w_period, seed)
    
    fy = sample_field(x, y + eps, z, w, octaves, lacunarity, gain, sigma,
                      warp_k1, warp_k2, s1, s2, w_period, seed)
    fy_neg = sample_field(x, y - eps, z, w, octaves, lacunarity, gain, sigma,
                          warp_k1, warp_k2, s1, s2, w_period, seed)
    
    fz = sample_field(x, y, z + eps, w, octaves, lacunarity, gain, sigma,
                      warp_k1, warp_k2, s1, s2, w_period, seed)
    fz_neg = sample_field(x, y, z - eps, w, octaves, lacunarity, gain, sigma,
                          warp_k1, warp_k2, s1, s2, w_period, seed)
    
    gx = (fx - fx_neg) / (2.0 * eps)
    gy = (fy - fy_neg) / (2.0 * eps)
    gz = (fz - fz_neg) / (2.0 * eps)
    
    return gx, gy, gz


class Field:
    """4D скалярное поле."""
    
    def __init__(self, cfg: dict, seed: int):
        self.seed = seed
        self.octaves = cfg['noise']['octaves']
        self.lacunarity = cfg['noise']['lacunarity']
        self.gain = cfg['noise']['gain']
        self.sigma = cfg['noise']['sigma']
        self.warp_k1 = cfg['noise']['warp_k1']
        self.warp_k2 = cfg['noise']['warp_k2']
        self.s1 = cfg['noise']['s1']
        self.s2 = cfg['noise']['s2']
        self.w_period = cfg['grid']['w_period']
    
    def sample(self, x: float, y: float, z: float, w: float) -> float:
        """Сэмплирование поля в точке."""
        return sample_field(
            x, y, z, w,
            self.octaves, self.lacunarity, self.gain,
            self.sigma, self.warp_k1, self.warp_k2,
            self.s1, self.s2, self.w_period, self.seed
        )
    
    def grad(self, x: float, y: float, z: float, w: float) -> Tuple[float, float, float]:
        """Градиент поля."""
        return field_gradient(
            x, y, z, w,
            self.octaves, self.lacunarity, self.gain,
            self.sigma, self.warp_k1, self.warp_k2,
            self.s1, self.s2, self.w_period, self.seed
        )

