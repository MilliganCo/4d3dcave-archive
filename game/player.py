"""Игрок и камера."""
import numpy as np
from core.math import Vec3
from core.physics import Physics


class Player:
    """Игрок."""
    
    def __init__(self, cfg: dict, start_pos: Vec3):
        self.physics = Physics(cfg)
        self.physics.position = start_pos
        
        # Камера
        self.camera_rot = Vec3(0, 0, 0)  # pitch, yaw, roll
        self.camera_height_offset = 1.6  # Высота камеры над центром капсулы
        
        # 4D координата w
        self.w = 0.0
        self.w_target = 0.0
        
        # Фонарик
        self.flashlight_mode = 0  # 0 = узкий, 1 = широкий
        self.flashlight_enabled = True
        
        self.cfg = cfg
    
    def get_camera_pos(self) -> Vec3:
        """Позиция камеры."""
        return self.physics.position + Vec3(0, self.camera_height_offset, 0)
    
    def get_camera_forward(self) -> Vec3:
        """Направление взгляда."""
        pitch = self.camera_rot.x
        yaw = self.camera_rot.y
        
        return Vec3(
            np.cos(yaw) * np.cos(pitch),
            np.sin(pitch),
            np.sin(yaw) * np.cos(pitch)
        ).normalize()
    
    def get_light_pos(self) -> Vec3:
        """Позиция источника света."""
        return self.get_camera_pos()
    
    def get_light_dir(self) -> Vec3:
        """Направление света."""
        return self.get_camera_forward()
    
    def get_light_angle(self) -> float:
        """Угол конуса фонарика."""
        if self.flashlight_mode == 0:
            return self.cfg['render']['flashlight_narrow_angle']
        else:
            return self.cfg['render']['flashlight_wide_angle']
    
    def get_light_range(self) -> float:
        """Дальность фонарика."""
        return self.cfg['render']['flashlight_range']
    
    def toggle_flashlight_mode(self):
        """Переключение режима фонарика."""
        self.flashlight_mode = 1 - self.flashlight_mode
    
    def update_w(self, delta: float):
        """Обновление координаты w."""
        self.w_target += delta
        # Плавная интерполяция (опционально)
        self.w = self.w_target
    
    def set_w(self, value: float):
        """Установка значения w."""
        self.w = value
        self.w_target = value

