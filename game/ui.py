"""UI и HUD."""
import time
from typing import Optional


class UI:
    """Пользовательский интерфейс."""
    
    def __init__(self):
        self.start_time = time.time()
        self.show_hud = True
    
    def get_time_elapsed(self) -> float:
        """Прошедшее время в секундах."""
        return time.time() - self.start_time
    
    def draw_hud(self, collected: int, total: int, w: float, w_period: float):
        """Отрисовка HUD (заглушка, в полной версии будет OpenGL текст)."""
        # В полной версии здесь будет отрисовка текста через библиотеку типа pyglet.text
        pass
    
    def draw_crosshair(self):
        """Отрисовка прицела."""
        # В полной версии здесь будет отрисовка крестика в центре экрана
        pass
    
    def draw_menu(self):
        """Отрисовка меню."""
        pass
    
    def draw_victory(self, time_elapsed: float, seed: int):
        """Отрисовка экрана победы."""
        pass

