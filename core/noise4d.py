"""4D OpenSimplex шум на numba."""
import numpy as np
from numba import njit
from typing import Tuple


# Константы для OpenSimplex
STRETCH_CONSTANT_4D = -0.138196601125011
SQUISH_CONSTANT_4D = 0.309016994374947
NORM_CONSTANT_4D = 30.0

# Градиенты для 4D
GRADIENTS_4D = np.array([
    [0, 1, 1, 1], [0, 1, 1, -1], [0, 1, -1, 1], [0, 1, -1, -1],
    [0, -1, 1, 1], [0, -1, 1, -1], [0, -1, -1, 1], [0, -1, -1, -1],
    [1, 0, 1, 1], [1, 0, 1, -1], [1, 0, -1, 1], [1, 0, -1, -1],
    [-1, 0, 1, 1], [-1, 0, 1, -1], [-1, 0, -1, 1], [-1, 0, -1, -1],
    [1, 1, 0, 1], [1, 1, 0, -1], [1, -1, 0, 1], [1, -1, 0, -1],
    [-1, 1, 0, 1], [-1, 1, 0, -1], [-1, -1, 0, 1], [-1, -1, 0, -1],
    [1, 1, 1, 0], [1, 1, -1, 0], [1, -1, 1, 0], [1, -1, -1, 0],
    [-1, 1, 1, 0], [-1, 1, -1, 0], [-1, -1, 1, 0], [-1, -1, -1, 0],
], dtype=np.int32)


@njit
def _permute(x: int) -> int:
    """Простая перестановка для seed."""
    x = ((x << 13) ^ x) & 0xFFFFFFFF
    return (x * (x * x * 15731 + 789221) + 1376312589) & 0xFFFFFFFF


@njit
def _permute_perm(x: int, seed: int) -> int:
    """Перестановка с seed."""
    x = ((x << 13) ^ x) & 0xFFFFFFFF
    return ((x * (x * x * 15731 + 789221) + 1376312589 + seed) & 0xFFFFFFFF) % 256


@njit
def _extrapolate(xsb: int, ysb: int, zsb: int, wsb: int, dx: float, dy: float, dz: float, dw: float, seed: int) -> float:
    """Экстраполяция градиента."""
    index = _permute_perm(
        _permute_perm(
            _permute_perm(
                _permute_perm(xsb, seed) ^ ysb, seed
            ) ^ zsb, seed
        ) ^ wsb, seed
    ) % len(GRADIENTS_4D)
    
    g = GRADIENTS_4D[index]
    return g[0] * dx + g[1] * dy + g[2] * dz + g[3] * dw


@njit
def opensimplex4d(x: float, y: float, z: float, w: float, seed: int = 0) -> float:
    """4D OpenSimplex шум, возвращает значение в [-1, 1]."""
    # Константы
    stretch = STRETCH_CONSTANT_4D
    squish = SQUISH_CONSTANT_4D
    
    # Выравнивание
    s = (x + y + z + w) * stretch
    xs = x + s
    ys = y + s
    zs = z + s
    ws = w + s
    
    # Целочисленные координаты
    xsb = int(np.floor(xs))
    ysb = int(np.floor(ys))
    zsb = int(np.floor(zs))
    wsb = int(np.floor(ws))
    
    # Дробные части
    xsi = xs - xsb
    ysi = ys - ysb
    zsi = zs - zsb
    wsi = ws - wsb
    
    # Расстояния от краев
    ssi = (xsi + ysi + zsi + wsi) * squish
    xi = xsi + ssi
    yi = ysi + ssi
    zi = zsi + ssi
    wi = wsi + ssi
    
    # Базовый слой
    value = 0.0
    
    # 32 ребра (упрощенная версия)
    for i in range(16):
        a = (i >> 0) & 1
        b = (i >> 1) & 1
        c = (i >> 2) & 1
        d = (i >> 3) & 1
        
        dx = xi - a - (b + c + d) * squish
        dy = yi - b - (a + c + d) * squish
        dz = zi - c - (a + b + d) * squish
        dw = wi - d - (a + b + c) * squish
        
        attn = 2.0 - (dx * dx + dy * dy + dz * dz + dw * dw)
        if attn > 0:
            attn *= attn
            value += attn * attn * _extrapolate(
                xsb + a, ysb + b, zsb + c, wsb + d,
                dx, dy, dz, dw, seed
            )
    
    return value / NORM_CONSTANT_4D


@njit
def fbm_4d(x: float, y: float, z: float, w: float, 
            octaves: int, lacunarity: float, gain: float, 
            sigma: float, seed: int) -> float:
    """Fractal Brownian Motion для 4D."""
    value = 0.0
    amplitude = 1.0
    frequency = 1.0 / sigma
    max_value = 0.0
    
    for i in range(octaves):
        value += amplitude * opensimplex4d(
            x * frequency, y * frequency, z * frequency, w * frequency, seed + i
        )
        max_value += amplitude
        amplitude *= gain
        frequency *= lacunarity
    
    return value / max_value if max_value > 0 else 0.0


@njit
def domain_warp_4d(x: float, y: float, z: float, w: float,
                   k1: float, k2: float, s1: float, s2: float,
                   octaves: int, lacunarity: float, gain: float,
                   sigma: float, seed: int) -> Tuple[float, float, float, float]:
    """Domain warping для 4D шума."""
    # Первый слой искажения
    dx1 = fbm_4d(x * s1, y * s1, z * s1, w * s1, octaves, lacunarity, gain, sigma, seed + 1000)
    dy1 = fbm_4d(x * s1 + 100, y * s1 + 100, z * s1 + 100, w * s1 + 100, octaves, lacunarity, gain, sigma, seed + 2000)
    dz1 = fbm_4d(x * s1 + 200, y * s1 + 200, z * s1 + 200, w * s1 + 200, octaves, lacunarity, gain, sigma, seed + 3000)
    dw1 = fbm_4d(x * s1 + 300, y * s1 + 300, z * s1 + 300, w * s1 + 300, octaves, lacunarity, gain, sigma, seed + 4000)
    
    # Второй слой
    dx2 = fbm_4d(dx1 * s2, dy1 * s2, dz1 * s2, dw1 * s2, octaves, lacunarity, gain, sigma, seed + 5000)
    dy2 = fbm_4d(dx1 * s2 + 100, dy1 * s2 + 100, dz1 * s2 + 100, dw1 * s2 + 100, octaves, lacunarity, gain, sigma, seed + 6000)
    dz2 = fbm_4d(dx1 * s2 + 200, dy1 * s2 + 200, dz1 * s2 + 200, dw1 * s2 + 200, octaves, lacunarity, gain, sigma, seed + 7000)
    dw2 = fbm_4d(dx1 * s2 + 300, dy1 * s2 + 300, dz1 * s2 + 300, dw1 * s2 + 300, octaves, lacunarity, gain, sigma, seed + 8000)
    
    # Комбинируем
    rx = x + k1 * dx1 + k2 * dx2
    ry = y + k1 * dy1 + k2 * dy2
    rz = z + k1 * dz1 + k2 * dz2
    rw = w + k1 * dw1 + k2 * dw2
    
    return rx, ry, rz, rw

