"""Состояния игры (FSM)."""
from enum import Enum


class GameState(Enum):
    """Состояния игры."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSE = "pause"
    VICTORY = "victory"


class StateManager:
    """Менеджер состояний."""
    
    def __init__(self):
        self.state = GameState.MENU
        self.prev_state = None
    
    def set_state(self, new_state: GameState):
        """Установка нового состояния."""
        self.prev_state = self.state
        self.state = new_state
    
    def get_state(self) -> GameState:
        """Получить текущее состояние."""
        return self.state

