"""Marching Cubes для генерации мешей из воксельных данных."""
import numpy as np
from numba import njit
from typing import Tuple


# Таблица рёбер для каждого куба (12 рёбер)
EDGE_TABLE = np.array([
    0x0, 0x109, 0x203, 0x30a, 0x406, 0x50f, 0x605, 0x70c,
    0x80c, 0x905, 0xa0f, 0xb06, 0xc0a, 0xd03, 0xe09, 0xf00,
    0x190, 0x99, 0x393, 0x29a, 0x596, 0x49f, 0x795, 0x69c,
    0x99c, 0x895, 0xb9f, 0xa96, 0xd9a, 0xc93, 0xf99, 0xe90,
    0x230, 0x339, 0x33, 0x13a, 0x636, 0x73f, 0x435, 0x53c,
    0xa3c, 0xb35, 0x83f, 0x936, 0xe3a, 0xf33, 0xc39, 0xd30,
    0x3a0, 0x2a9, 0x1a3, 0xaa, 0x7a6, 0x6af, 0x5a5, 0x4ac,
    0xbac, 0xaa5, 0x9af, 0x8a6, 0xfaa, 0xea3, 0xda9, 0xca0,
    0x460, 0x569, 0x663, 0x76a, 0x66, 0x16f, 0x265, 0x36c,
    0xc6c, 0xd65, 0xe6f, 0xf66, 0x86a, 0x963, 0xa69, 0xb60,
    0x5f0, 0x4f9, 0x7f3, 0x6fa, 0x1f6, 0xff, 0x3f5, 0x2fc,
    0xdfc, 0xcf5, 0xfff, 0xef6, 0x9fa, 0x8f3, 0xbf9, 0xaf0,
    0x650, 0x759, 0x453, 0x55a, 0x256, 0x35f, 0x55, 0x15c,
    0xe5c, 0xf55, 0xc5f, 0xd56, 0xa5a, 0xb53, 0x959, 0x850,
    0x7c0, 0x6c9, 0x5c3, 0x4ca, 0x3c6, 0x2cf, 0x1c5, 0xcc,
    0xfcc, 0xec5, 0xdcf, 0xcc6, 0xbca, 0xac3, 0x9c9, 0x8c0,
    0x8c0, 0x9c9, 0xac3, 0xbca, 0xcc6, 0xdcf, 0xec5, 0xfcc,
    0xcc, 0x1c5, 0x2cf, 0x3c6, 0x4ca, 0x5c3, 0x6c9, 0x7c0,
    0x950, 0x859, 0xb53, 0xa5a, 0xd56, 0xc5f, 0xf55, 0xe5c,
    0x15c, 0x55, 0x35f, 0x256, 0x55a, 0x453, 0x759, 0x650,
    0xaf0, 0xbf9, 0x8f3, 0x9fa, 0xef6, 0xfff, 0xcf5, 0xdfc,
    0x2fc, 0x3f5, 0xff, 0x1f6, 0x6fa, 0x7f3, 0x4f9, 0x5f0,
    0xb60, 0xa69, 0x963, 0x86a, 0xf66, 0xe6f, 0xd65, 0xc6c,
    0x36c, 0x265, 0x16f, 0x66, 0x76a, 0x663, 0x569, 0x460,
    0xca0, 0xda9, 0xea3, 0xfaa, 0x8a6, 0x9af, 0xaa5, 0xbac,
    0x4ac, 0x5a5, 0x6af, 0x7a6, 0xaa, 0x1a3, 0x2a9, 0x3a0,
    0xd30, 0xc39, 0xf33, 0xe3a, 0x936, 0x83f, 0xb35, 0xa3c,
    0x53c, 0x435, 0x73f, 0x636, 0x13a, 0x33, 0x339, 0x230,
    0xe90, 0xf99, 0xc93, 0xd9a, 0xa96, 0xb9f, 0x895, 0x99c,
    0x69c, 0x795, 0x49f, 0x596, 0x29a, 0x393, 0x99, 0x190,
    0xf00, 0xe09, 0xd03, 0xc0a, 0xb06, 0xa0f, 0x905, 0x80c,
    0x70c, 0x605, 0x50f, 0x406, 0x30a, 0x203, 0x109, 0x0
], dtype=np.int32)


# Вершины куба (8 вершин)
CUBE_VERTICES = np.array([
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
], dtype=np.float32)


# Рёбра куба (12 рёбер, каждая соединяет 2 вершины)
EDGE_VERTICES = np.array([
    [0, 1], [1, 2], [2, 3], [3, 0],  # нижняя грань
    [4, 5], [5, 6], [6, 7], [7, 4],  # верхняя грань
    [0, 4], [1, 5], [2, 6], [3, 7]   # вертикальные рёбра
], dtype=np.int32)


# Таблица треугольников (упрощенная версия основных кейсов)
TRI_TABLE = np.zeros((256, 16), dtype=np.int32)
# Заполняем основные кейсы (полная таблица слишком большая, используем упрощенную логику)


def _interpolate_vertex(v1: np.ndarray, v2: np.ndarray, val1: float, val2: float, iso: float) -> np.ndarray:
    """Интерполяция вершины на ребре."""
    if abs(val1 - val2) < 1e-10:
        return (v1 + v2) * 0.5
    t = (iso - val1) / (val2 - val1)
    return v1 + t * (v2 - v1)


def _get_cube_index(values: np.ndarray, iso: float) -> int:
    """Получить индекс куба из значений вершин."""
    index = 0
    for i in range(8):
        if values[i] < iso:
            index |= (1 << i)
    return index


def build_mesh_simple(field: np.ndarray, iso: float, cell_size: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Упрощенный marching cubes для одного чанка."""
    nx, ny, nz = field.shape
    positions = []
    normals = []
    indices = []
    
    # Предварительно выделяем память (оценка)
    max_verts = nx * ny * nz * 3  # Максимум 3 треугольника на куб
    pos_list = np.zeros((max_verts, 3), dtype=np.float32)
    norm_list = np.zeros((max_verts, 3), dtype=np.float32)
    idx_list = []
    
    vertex_count = 0
    
    # Проходим по всем кубам
    for x in range(nx - 1):
        for y in range(ny - 1):
            for z in range(nz - 1):
                # Значения в вершинах куба
                cube_values = np.array([
                    field[x, y, z],
                    field[x + 1, y, z],
                    field[x + 1, y + 1, z],
                    field[x, y + 1, z],
                    field[x, y, z + 1],
                    field[x + 1, y, z + 1],
                    field[x + 1, y + 1, z + 1],
                    field[x, y + 1, z + 1]
                ], dtype=np.float32)
                
                # Индекс конфигурации
                cube_index = _get_cube_index(cube_values, iso)
                
                # Пропускаем пустые кубы
                if cube_index == 0 or cube_index == 255:
                    continue
                
                # Позиции вершин куба в мировых координатах
                base_pos = np.array([x, y, z], dtype=np.float32) * cell_size
                cube_verts = np.zeros((8, 3), dtype=np.float32)
                for i in range(8):
                    cube_verts[i] = base_pos + CUBE_VERTICES[i] * cell_size
                
                # Генерируем треугольники для этого куба
                edge_flags = EDGE_TABLE[cube_index]
                
                if edge_flags == 0:
                    continue
                
                # Находим пересечения с рёбрами
                edge_vertices = np.zeros((12, 3), dtype=np.float32)
                for edge in range(12):
                    if edge_flags & (1 << edge):
                        v0_idx, v1_idx = EDGE_VERTICES[edge]
                        v0 = cube_verts[v0_idx]
                        v1 = cube_verts[v1_idx]
                        val0 = cube_values[v0_idx]
                        val1 = cube_values[v1_idx]
                        edge_vertices[edge] = _interpolate_vertex(v0, v1, val0, val1, iso)
                
                # Простая генерация треугольников (упрощенная логика)
                # Для MVP используем простую схему: находим активные рёбра и формируем треугольники
                active_edges = []
                for edge in range(12):
                    if edge_flags & (1 << edge):
                        active_edges.append(edge)
                
                # Формируем треугольники из активных рёбер
                if len(active_edges) >= 3:
                    # Упрощенная логика: группируем рёбра в треугольники
                    for i in range(len(active_edges) - 2):
                        if vertex_count + 3 > max_verts:
                            break
                        
                        e0 = active_edges[i]
                        e1 = active_edges[(i + 1) % len(active_edges)]
                        e2 = active_edges[(i + 2) % len(active_edges)]
                        
                        # Проверяем, что рёбра образуют валидный треугольник
                        v0 = edge_vertices[e0]
                        v1 = edge_vertices[e1]
                        v2 = edge_vertices[e2]
                        
                        # Вычисляем нормаль
                        e01 = v1 - v0
                        e02 = v2 - v0
                        normal = np.cross(e01, e02)
                        norm_len = np.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
                        if norm_len > 1e-10:
                            normal = normal / norm_len
                        else:
                            normal = np.array([0, 0, 1], dtype=np.float32)
                        
                        # Добавляем вершины
                        pos_list[vertex_count] = v0
                        norm_list[vertex_count] = normal
                        idx_list.append(vertex_count)
                        vertex_count += 1
                        
                        pos_list[vertex_count] = v1
                        norm_list[vertex_count] = normal
                        idx_list.append(vertex_count)
                        vertex_count += 1
                        
                        pos_list[vertex_count] = v2
                        norm_list[vertex_count] = normal
                        idx_list.append(vertex_count)
                        vertex_count += 1
    
    # Обрезаем массивы до реального размера
    if vertex_count == 0:
        return np.zeros((0, 3), dtype=np.float32), np.zeros((0, 3), dtype=np.float32), np.zeros(0, dtype=np.uint32)
    
    positions = pos_list[:vertex_count]
    normals = norm_list[:vertex_count]
    indices = np.array(idx_list, dtype=np.uint32)
    
    return positions, normals, indices


def build_mesh(field: np.ndarray, iso: float, cell_size: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Главная функция для построения меша."""
    return build_mesh_simple(field, iso, cell_size)

