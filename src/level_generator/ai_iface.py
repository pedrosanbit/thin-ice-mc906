# src/level_generator/human_iface.py

import pygame
from src.mapping import *
from src.utils import init_screen

from .actions import (
    MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT,
    PLACE_COIN, PLACE_KEY, PLACE_LOCK, PLACE_TELEPORT,
    PLACE_FINISH, DISCARD
)
from .core import LevelCore
from .movement import *

class LevelCreatorEnv(LevelCore):
    ACTIONS = (
        MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT,
        PLACE_COIN, PLACE_KEY, PLACE_LOCK, PLACE_TELEPORT,
        PLACE_FINISH, DISCARD
    )

    def step(self, action_idx: int) -> bool:
        """Recebe um inteiro 0-9, aplica a ação e devolve
        True se a ação foi executada com sucesso."""
        action = self.ACTIONS[action_idx]
        valid = apply_action(self, action)
        if pygame.display.get_init():
            draw_level(self)      
        return valid

    def reset(self):
        """Reinicia o nível (útil para treino)."""
        self.__init__()
