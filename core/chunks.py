"""Менеджер чанков для управления геометрией."""
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from .field import Field
from .mc import build_mesh


@dataclass
class MeshData:
    """Данные меша."""
    coord: Tuple[int, int, int]
    w_bin: int
    positions: np.ndarray  # float32 Nx3
    normals: np.ndarray    # float32 Nx3
    indices: np.ndarray    # uint32 M


class ChunkManager:
    """Менеджер чанков для генерации и кэширования геометрии."""
    
    def __init__(self, field: Field, cfg: dict):
        self.field = field
        self.cfg = cfg
        self.chunk_size = cfg['grid']['chunk']
        self.cell_size = cfg['grid']['cell_size']
        self.iso = cfg['grid']['iso']
        self.w_delta = cfg['grid']['w_delta']
        
        # Кэш мешей: ключ = (coord, w_bin)
        self.mesh_cache: Dict[Tuple[Tuple[int, int, int], int], MeshData] = {}
        
        # Активные чанки
        self.active_chunks: List[Tuple[int, int, int]] = []
    
    def _world_to_chunk(self, pos: np.ndarray) -> Tuple[int, int, int]:
        """Преобразование мировых координат в координаты чанка."""
        chunk_x = int(np.floor(pos[0] / (self.chunk_size * self.cell_size)))
        chunk_y = int(np.floor(pos[1] / (self.chunk_size * self.cell_size)))
        chunk_z = int(np.floor(pos[2] / (self.chunk_size * self.cell_size)))
        return (chunk_x, chunk_y, chunk_z)
    
    def _w_to_bin(self, w: float) -> int:
        """Округление w до бина."""
        return int(np.round(w / self.w_delta))
    
    def _generate_chunk(self, coord: Tuple[int, int, int], w: float) -> Optional[MeshData]:
        """Генерация меша для чанка."""
        w_bin = self._w_to_bin(w)
        cache_key = (coord, w_bin)
        
        # Проверяем кэш
        if cache_key in self.mesh_cache:
            return self.mesh_cache[cache_key]
        
        # Генерируем поле для чанка
        chunk_x, chunk_y, chunk_z = coord
        size = self.chunk_size
        
        # Мировые координаты начала чанка
        world_x0 = chunk_x * size * self.cell_size
        world_y0 = chunk_y * size * self.cell_size
        world_z0 = chunk_z * size * self.cell_size
        
        # Генерируем воксельное поле
        field_data = np.zeros((size + 1, size + 1, size + 1), dtype=np.float32)
        
        for i in range(size + 1):
            for j in range(size + 1):
                for k in range(size + 1):
                    x = world_x0 + i * self.cell_size
                    y = world_y0 + j * self.cell_size
                    z = world_z0 + k * self.cell_size
                    field_data[i, j, k] = self.field.sample(x, y, z, w)
        
        # Строим меш
        positions, normals, indices = build_mesh(field_data, self.iso, self.cell_size)
        
        # Проверяем лимит треугольников
        max_tris = self.cfg['render']['max_tris']
        if len(indices) > max_tris * 3:
            # Упрощаем меш (просто пропускаем некоторые треугольники)
            step = len(indices) // (max_tris * 3)
            if step > 1:
                indices = indices[::step]
                positions = positions[:len(indices)]
                normals = normals[:len(indices)]
        
        mesh = MeshData(
            coord=coord,
            w_bin=w_bin,
            positions=positions,
            normals=normals,
            indices=indices
        )
        
        # Сохраняем в кэш
        self.mesh_cache[cache_key] = mesh
        
        return mesh
    
    def update(self, player_pos: np.ndarray, w: float) -> None:
        """Обновление активных чанков вокруг игрока."""
        # Определяем центральный чанк
        center_chunk = self._world_to_chunk(player_pos)
        
        # Активные чанки: 2x2x2 вокруг центра
        new_active = []
        for dx in range(-1, 1):
            for dy in range(-1, 1):
                for dz in range(-1, 1):
                    chunk_coord = (
                        center_chunk[0] + dx,
                        center_chunk[1] + dy,
                        center_chunk[2] + dz
                    )
                    new_active.append(chunk_coord)
        
        # Генерируем недостающие чанки
        for coord in new_active:
            if coord not in self.active_chunks:
                self._generate_chunk(coord, w)
        
        self.active_chunks = new_active
    
    def get_drawables(self, w: float) -> List[MeshData]:
        """Получить список мешей для отрисовки."""
        w_bin = self._w_to_bin(w)
        drawables = []
        
        for coord in self.active_chunks:
            cache_key = (coord, w_bin)
            if cache_key in self.mesh_cache:
                mesh = self.mesh_cache[cache_key]
                if len(mesh.indices) > 0:
                    drawables.append(mesh)
        
        return drawables
    
    def clear_cache(self, max_size: int = 100) -> None:
        """Очистка кэша при превышении лимита."""
        if len(self.mesh_cache) > max_size:
            # Удаляем старые записи (простая стратегия: удаляем половину)
            keys_to_remove = list(self.mesh_cache.keys())[:len(self.mesh_cache) // 2]
            for key in keys_to_remove:
                del self.mesh_cache[key]

