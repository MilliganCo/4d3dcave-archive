"""Мир игры."""
import numpy as np
from core.field import Field
from core.chunks import ChunkManager
from core.gen import find_start_point, poisson_disk_sample
from core.math import Vec3
from .pickups import Pickups
from .exit_portal import ExitPortal
from .player import Player


class World:
    """Мир игры."""
    
    def __init__(self, cfg: dict, seed: int):
        self.cfg = cfg
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        
        # Генерация поля
        self.field = Field(cfg, seed)
        self.chunk_manager = ChunkManager(self.field, cfg)
        
        # Генерация стартовой точки
        start_pos = find_start_point(self.field, cfg, self.rng)
        
        # Игрок
        self.player = Player(cfg, start_pos)
        
        # Коллектиблы
        n_pickups = cfg['gameplay']['pickups']
        pickup_positions = poisson_disk_sample(
            self.field, cfg, n_pickups, start_pos, self.rng
        )
        self.pickups = Pickups(pickup_positions)
        
        # Выходной портал (рядом со стартом)
        exit_pos = start_pos + Vec3(3, 0, 3)
        self.exit_portal = ExitPortal(exit_pos)
    
    def regenerate(self, seed: int):
        """Регенерация мира с новым seed."""
        self.__init__(self.cfg, seed)
    
    def update(self, dt: float):
        """Обновление мира."""
        # Обновление коллектиблов
        collected = self.pickups.update(self.player.get_camera_pos())
        
        # Активация портала при сборе всех
        if self.pickups.is_complete() and not self.exit_portal.active:
            self.exit_portal.activate()
        
        # Обновление чанков
        self.chunk_manager.update(
            self.player.physics.position.to_array(),
            self.player.w
        )
    
    def collect_at(self, pos: Vec3, radius: float = 1.5) -> int:
        """Сбор коллектиблов в радиусе."""
        return self.pickups.update(pos, radius)
    
    def completed(self) -> bool:
        """Проверка завершения уровня."""
        return self.pickups.is_complete() and self.exit_portal.check_intersection(
            self.player.get_camera_pos()
        )
    
    def get_drawable_meshes(self):
        """Получить меши для отрисовки."""
        return self.chunk_manager.get_drawables(self.player.w)

