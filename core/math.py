"""Математические утилиты: векторы, матрицы."""
import numpy as np
from typing import Tuple


class Vec3:
    """3D вектор."""
    __slots__ = ('x', 'y', 'z')
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __add__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vec3':
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar: float) -> 'Vec3':
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> 'Vec3':
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __neg__(self) -> 'Vec3':
        return Vec3(-self.x, -self.y, -self.z)
    
    def dot(self, other: 'Vec3') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'Vec3') -> 'Vec3':
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self) -> float:
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def length_sq(self) -> float:
        return self.x**2 + self.y**2 + self.z**2
    
    def normalize(self) -> 'Vec3':
        l = self.length()
        if l < 1e-10:
            return Vec3(0, 0, 1)
        return self / l
    
    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=np.float32)
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'Vec3':
        return cls(arr[0], arr[1], arr[2])
    
    def __repr__(self) -> str:
        return f"Vec3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"


def look_at(eye: Vec3, target: Vec3, up: Vec3 = None) -> np.ndarray:
    """Матрица вида look-at."""
    if up is None:
        up = Vec3(0, 1, 0)
    
    forward = (target - eye).normalize()
    right = forward.cross(up).normalize()
    up = right.cross(forward).normalize()
    
    mat = np.eye(4, dtype=np.float32)
    mat[0, :3] = right.to_array()
    mat[1, :3] = up.to_array()
    mat[2, :3] = (-forward).to_array()
    mat[0, 3] = -right.dot(eye)
    mat[1, 3] = -up.dot(eye)
    mat[2, 3] = forward.dot(eye)
    return mat


def perspective(fov: float, aspect: float, near: float, far: float) -> np.ndarray:
    """Матрица перспективной проекции."""
    f = 1.0 / np.tan(np.radians(fov) / 2.0)
    mat = np.zeros((4, 4), dtype=np.float32)
    mat[0, 0] = f / aspect
    mat[1, 1] = f
    mat[2, 2] = (far + near) / (near - far)
    mat[2, 3] = (2 * far * near) / (near - far)
    mat[3, 2] = -1.0
    return mat


def translate(x: float, y: float, z: float) -> np.ndarray:
    """Матрица перемещения."""
    mat = np.eye(4, dtype=np.float32)
    mat[0, 3] = x
    mat[1, 3] = y
    mat[2, 3] = z
    return mat


def rotate_x(angle: float) -> np.ndarray:
    """Матрица поворота вокруг X."""
    c = np.cos(angle)
    s = np.sin(angle)
    mat = np.eye(4, dtype=np.float32)
    mat[1, 1] = c
    mat[1, 2] = -s
    mat[2, 1] = s
    mat[2, 2] = c
    return mat


def rotate_y(angle: float) -> np.ndarray:
    """Матрица поворота вокруг Y."""
    c = np.cos(angle)
    s = np.sin(angle)
    mat = np.eye(4, dtype=np.float32)
    mat[0, 0] = c
    mat[0, 2] = s
    mat[2, 0] = -s
    mat[2, 2] = c
    return mat


def rotate_z(angle: float) -> np.ndarray:
    """Матрица поворота вокруг Z."""
    c = np.cos(angle)
    s = np.sin(angle)
    mat = np.eye(4, dtype=np.float32)
    mat[0, 0] = c
    mat[0, 1] = -s
    mat[1, 0] = s
    mat[1, 1] = c
    return mat

