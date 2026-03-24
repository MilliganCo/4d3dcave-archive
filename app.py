"""Главный файл приложения."""
import yaml
import numpy as np
import glfw
from pathlib import Path

from render.window import Window
from render.renderer import Renderer
from game.state import GameState, StateManager
from game.world import World
from game.ui import UI
from core.math import Vec3


class Game:
    """Главный класс игры."""
    
    def __init__(self):
        # Загрузка конфигурации
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            self.cfg = yaml.safe_load(f)
        
        # Окно и рендерер
        self.window = Window(1280, 720, "4D Cave: Найди все огни")
        self.renderer = Renderer(self.window)
        
        # Состояние игры
        self.state_manager = StateManager()
        self.state_manager.set_state(GameState.PLAYING)  # Начинаем сразу в игре
        self.ui = UI()
        
        # Мир
        self.world = None
        self._init_world()
        
        # Таймер
        self.last_time = None
        self.dt = 1.0 / 60.0
    
    def _init_world(self):
        """Инициализация мира."""
        seed = self.cfg.get('seed', 12345)
        self.world = World(self.cfg, seed)
    
    def _handle_input(self):
        """Обработка ввода."""
        # Клавиши движения
        move_forward = 0.0
        move_right = 0.0
        
        if self.window.get_key(glfw.KEY_W):
            move_forward += 1.0
        if self.window.get_key(glfw.KEY_S):
            move_forward -= 1.0
        if self.window.get_key(glfw.KEY_A):
            move_right -= 1.0
        if self.window.get_key(glfw.KEY_D):
            move_right += 1.0
        
        # Мышь
        mouse_delta = self.window.get_mouse_delta()
        sensitivity = self.cfg['player']['mouse_sensitivity']
        self.world.player.camera_rot.y += mouse_delta[0] * sensitivity
        self.world.player.camera_rot.x -= mouse_delta[1] * sensitivity
        self.world.player.camera_rot.x = np.clip(
            self.world.player.camera_rot.x, -np.pi/2 + 0.1, np.pi/2 - 0.1
        )
        
        # W координата
        w_delta = 0.0
        if self.window.get_key(glfw.KEY_Q):
            w_delta = -self.cfg['grid']['w_delta']
        if self.window.get_key(glfw.KEY_E):
            w_delta = self.cfg['grid']['w_delta']
        
        wheel = self.window.get_mouse_wheel()
        if wheel != 0:
            w_delta = wheel * self.cfg['grid']['w_delta'] * 2
            # Сбрасываем колесо после использования
            self.window.mouse_wheel = 0.0
        
        if w_delta != 0:
            self.world.player.update_w(w_delta)
        
        # Другие клавиши
        if self.window.get_key(glfw.KEY_F):
            self.world.player.toggle_flashlight_mode()
        
        if self.window.get_key(glfw.KEY_R):
            self._init_world()
        
        if self.window.get_key(glfw.KEY_ESCAPE):
            if self.state_manager.get_state() == GameState.PLAYING:
                self.state_manager.set_state(GameState.PAUSE)
            elif self.state_manager.get_state() == GameState.PAUSE:
                self.state_manager.set_state(GameState.PLAYING)
        
        # Прыжок
        jump = self.window.get_key(glfw.KEY_SPACE)
        crouch = self.window.get_key(glfw.KEY_LEFT_CONTROL) or self.window.get_key(glfw.KEY_RIGHT_CONTROL)
        
        # Преобразование направления движения относительно камеры
        yaw = self.world.player.camera_rot.y
        # Forward направление камеры (вдоль взгляда)
        forward_dir = Vec3(
            np.cos(yaw),
            0,
            np.sin(yaw)
        )
        # Right направление (перпендикулярно forward)
        right_dir = Vec3(
            -np.sin(yaw),
            0,
            np.cos(yaw)
        )
        
        # Комбинируем направления
        move_direction = forward_dir * move_forward + right_dir * move_right
        if move_direction.length() > 0:
            move_direction = move_direction.normalize()
        
        # Физика
        self.world.player.physics.step(
            move_direction, Vec3(0, 0, 0), jump, crouch, self.dt
        )
    
    def _update(self, dt: float):
        """Обновление игры."""
        if self.state_manager.get_state() == GameState.PLAYING:
            self.world.update(dt)
            
            # Проверка победы
            if self.world.completed():
                self.state_manager.set_state(GameState.VICTORY)
    
    def _render(self):
        """Отрисовка."""
        if self.state_manager.get_state() == GameState.PLAYING:
            player = self.world.player
            
            # Получаем меши
            meshes = self.world.get_drawable_meshes()
            gpu_meshes = []
            for mesh in meshes:
                if len(mesh.indices) > 0:  # Пропускаем пустые меши
                    gpu_mesh = self.renderer.upload_mesh(mesh)
                    gpu_meshes.append(gpu_mesh)
            
            # Данные для свечений
            glows = self.world.pickups.get_glows()
            if self.world.exit_portal.active:
                glows.append(self.world.exit_portal.get_glow_data())
            
            # Отрисовка
            if gpu_meshes:
                self.renderer.draw(
                    gpu_meshes,
                    player.get_camera_pos(),
                    (player.camera_rot.x, player.camera_rot.y, 0),
                    player.get_light_pos(),
                    player.get_light_dir(),
                    player.get_light_angle(),
                    player.get_light_range(),
                    glows,
                    self.cfg['render']['fog_distance']
                )
            
            # Очистка кэша GPU мешей периодически
            self.renderer.clear_gpu_cache()
    
    def run(self):
        """Главный цикл игры."""
        import time
        self.last_time = time.time()
        
        while not self.window.should_close():
            # Вычисление dt
            current_time = time.time()
            if self.last_time is not None:
                self.dt = current_time - self.last_time
                self.dt = min(self.dt, 1.0 / 30.0)  # Ограничение максимального dt
            self.last_time = current_time
            
            # Обработка ввода
            self._handle_input()
            
            # Обновление
            self._update(self.dt)
            
            # Отрисовка
            self._render()
            
            # Обновление окна
            self.window.swap_buffers()
            self.window.poll_events()
        
        # Очистка
        self.renderer.cleanup()
        self.window.cleanup()


def main():
    """Точка входа."""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

