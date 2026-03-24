"""Рендерер на moderngl."""
import moderngl
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from .window import Window
from core.chunks import MeshData
from core.math import Vec3, look_at, perspective


def _load_shader(path: str) -> str:
    """Загрузка шейдера из файла."""
    shader_path = Path(__file__).parent / path
    with open(shader_path, 'r') as f:
        return f.read()


class GpuMesh:
    """GPU меш."""
    def __init__(self, ctx: moderngl.Context, mesh: MeshData, program: moderngl.Program):
        self.ctx = ctx
        self.program = program
        self.index_count = len(mesh.indices)
        
        if len(mesh.positions) == 0:
            self.vbo = None
            self.ibo = None
            self.vao = None
            return
        
        # Interleaved buffer
        interleaved = np.zeros(len(mesh.positions), dtype=[
            ('position', np.float32, 3),
            ('normal', np.float32, 3)
        ])
        interleaved['position'] = mesh.positions
        interleaved['normal'] = mesh.normals
        
        indices_data = mesh.indices.astype(np.uint32).tobytes()
        
        self.vbo = ctx.buffer(interleaved.tobytes())
        self.ibo = ctx.buffer(indices_data)
        
        # Создаем VAO с индексным буфером
        # Используем vertex_array вместо simple_vertex_array для поддержки индексов
        # Формат: 3 float для position, затем 3 float для normal
        # stride = 6 * 4 байта (24 байта на вершину)
        self.vao = ctx.vertex_array(
            program,
            [
                (self.vbo, '3f 3f', 'position', 'normal')
            ],
            index_buffer=self.ibo
        )
    
    def release(self):
        if self.vbo:
            self.vbo.release()
        if self.ibo:
            self.ibo.release()
        if self.vao:
            self.vao.release()
    
    def render(self):
        """Отрисовка меша."""
        if self.vao and self.index_count > 0:
            self.vao.render()


class Renderer:
    """Рендерер."""
    
    def __init__(self, window: Window):
        self.window = window
        self.ctx = moderngl.create_context()
        
        # Шейдеры
        cave_vert = _load_shader('shaders/cave.vert')
        cave_frag = _load_shader('shaders/cave.frag')
        
        self.cave_program = self.ctx.program(
            vertex_shader=cave_vert,
            fragment_shader=cave_frag
        )
        
        # Кэш GPU мешей: ключ = (coord, w_bin)
        self.gpu_mesh_cache: Dict[Tuple[Tuple[int, int, int], int], GpuMesh] = {}
        
        # Настройки
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)
    
    def upload_mesh(self, mesh: MeshData) -> GpuMesh:
        """Загрузка меша в GPU с кэшированием."""
        cache_key = (mesh.coord, mesh.w_bin)
        
        # Проверяем кэш
        if cache_key in self.gpu_mesh_cache:
            return self.gpu_mesh_cache[cache_key]
        
        # Создаем новый GPU меш
        gpu_mesh = GpuMesh(self.ctx, mesh, self.cave_program)
        self.gpu_mesh_cache[cache_key] = gpu_mesh
        
        return gpu_mesh
    
    def clear_gpu_cache(self, max_size: int = 50):
        """Очистка кэша GPU мешей."""
        if len(self.gpu_mesh_cache) > max_size:
            # Удаляем старые записи
            keys_to_remove = list(self.gpu_mesh_cache.keys())[:len(self.gpu_mesh_cache) // 2]
            for key in keys_to_remove:
                self.gpu_mesh_cache[key].release()
                del self.gpu_mesh_cache[key]
    
    def draw(self, meshes: List[GpuMesh], camera_pos: Vec3, camera_rot: tuple,
             player_light_pos: Vec3, player_light_dir: Vec3,
             light_angle: float, light_range: float,
             glows: List[tuple], fog_distance: float):
        """Отрисовка сцены."""
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        
        # Матрицы камеры
        pitch, yaw, _ = camera_rot
        target = camera_pos + Vec3(
            np.cos(yaw) * np.cos(pitch),
            np.sin(pitch),
            np.sin(yaw) * np.cos(pitch)
        )
        view = look_at(camera_pos, target)
        proj = perspective(75.0, self.window.get_aspect(), 0.1, 100.0)
        mvp = proj @ view
        
        # Отрисовка пещеры
        self.cave_program['mvp'].write(mvp.T.astype(np.float32).tobytes())
        self.cave_program['model'].write(np.eye(4, dtype=np.float32).tobytes())
        self.cave_program['light_pos'].write(player_light_pos.to_array().astype(np.float32).tobytes())
        self.cave_program['light_dir'].write(player_light_dir.to_array().astype(np.float32).tobytes())
        self.cave_program['light_angle'].value = np.radians(light_angle)
        self.cave_program['light_range'].value = light_range
        self.cave_program['light_color'].write(np.array([1.0, 1.0, 0.9], dtype=np.float32).tobytes())
        self.cave_program['fog_distance'].value = fog_distance
        self.cave_program['fog_color'].write(np.array([0.0, 0.0, 0.0], dtype=np.float32).tobytes())
        
        for gpu_mesh in meshes:
            gpu_mesh.render()
        
        # Отрисовка свечений (упрощенная)
        # В полной версии здесь будет отдельный шейдер для свечений
    
    def cleanup(self):
        # Освобождаем все кэшированные GPU меши
        for gpu_mesh in self.gpu_mesh_cache.values():
            gpu_mesh.release()
        self.gpu_mesh_cache.clear()
        self.ctx.release()

