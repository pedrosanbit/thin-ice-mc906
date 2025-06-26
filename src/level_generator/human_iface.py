# src/level_generator/human_iface.py

import pygame
from src.mapping import *
from .actions import *
from src.utils import init_screen

from .core import LevelCore
from .movement import *

class LevelCreatorHuman(LevelCore):
    def __init__(self, load_folder = 'custom_created_human'):
        super().__init__(load_folder)

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    close_display()
                    return

            keys = pygame.key.get_pressed()
            action = None
            if keys[pygame.K_UP]: action = MOVE_UP
            elif keys[pygame.K_DOWN]: action = MOVE_DOWN
            elif keys[pygame.K_LEFT]: action = MOVE_LEFT
            elif keys[pygame.K_RIGHT]: action = MOVE_RIGHT
            elif keys[pygame.K_1]: action = PLACE_COIN
            elif keys[pygame.K_2]: action = PLACE_KEY
            elif keys[pygame.K_3]: action = PLACE_LOCK
            elif keys[pygame.K_4]: action = PLACE_TELEPORT
            elif keys[pygame.K_RETURN]: action = PLACE_FINISH
            elif keys[pygame.K_ESCAPE]: action = DISCARD
            else: action = None

            if action is not None:
                valid = apply_action(self, action)
                if not valid:        # cancelou/terminou
                    return

            if pygame.display.get_init():
                draw_level(self)
