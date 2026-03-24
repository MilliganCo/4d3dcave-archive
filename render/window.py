"""Окно и обработка ввода."""
import glfw
import numpy as np
from typing import Optional, Callable


class Window:
    """Окно GLFW для рендеринга."""
    
    def __init__(self, width: int = 1280, height: int = 720, title: str = "4D Cave"):
        self.width = width
        self.height = height
        self.title = title
        
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create window")
        
        glfw.make_context_current(self.window)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        
        # Состояние ввода
        self.keys = {}
        self.mouse_pos = (0.0, 0.0)
        self.mouse_delta = (0.0, 0.0)
        self.mouse_wheel = 0.0
        
        # Callbacks
        glfw.set_key_callback(self.window, self._key_callback)
        glfw.set_cursor_pos_callback(self.window, self._cursor_callback)
        glfw.set_scroll_callback(self.window, self._scroll_callback)
    
    def _key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.keys[key] = True
        elif action == glfw.RELEASE:
            self.keys[key] = False
    
    def _cursor_callback(self, window, xpos, ypos):
        if hasattr(self, '_last_mouse_pos'):
            self.mouse_delta = (
                xpos - self._last_mouse_pos[0],
                ypos - self._last_mouse_pos[1]
            )
        else:
            self.mouse_delta = (0.0, 0.0)
        
        self.mouse_pos = (xpos, ypos)
        self._last_mouse_pos = (xpos, ypos)
    
    def _scroll_callback(self, window, xoffset, yoffset):
        # Накопление значения колеса мыши
        self.mouse_wheel += yoffset
    
    def should_close(self) -> bool:
        return glfw.window_should_close(self.window)
    
    def swap_buffers(self):
        glfw.swap_buffers(self.window)
    
    def poll_events(self):
        glfw.poll_events()
        # Сбрасываем delta после обработки
        self.mouse_delta = (0.0, 0.0)
        # mouse_wheel теперь сбрасывается после использования в app.py
    
    def get_key(self, key: int) -> bool:
        return self.keys.get(key, False)
    
    def get_mouse_delta(self) -> tuple:
        return self.mouse_delta
    
    def get_mouse_wheel(self) -> float:
        return self.mouse_wheel
    
    def get_aspect(self) -> float:
        return self.width / self.height if self.height > 0 else 1.0
    
    def cleanup(self):
        glfw.terminate()

