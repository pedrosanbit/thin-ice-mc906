# src/level_generation/level_creator.py

import pygame
import random
from src.mapping import *
from src.utils import init_screen
from src.level_generator.drawing import *
from src.level_generator.movement import *
from src.level_generator.objects import *
from src.level_generator.teleport import *
from src.level_generator.validation import *
from src.level_generator.save import *
from src.level_generator.actions import *

class LevelCreator:
    def __init__(self):
        self.Map = Map
        self.screen, self.font = init_screen()
        self.grid = [[Map.WALL.value for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.start = self._get_random_start()
        self.grid[self.start[1]][self.start[0]] = Map.THIN_ICE.value
        self.player_x, self.player_y = self.start
        self.original_start = self.start
        self.forbidden_area = set()

        self.coin_bags = []
        self.keys = []
        self.locks = []
        self.teleports = []
        self.teleport_stage = 0
        self.teleport_temp = None
        self.lock_placed = False
        self.coin_placed = False
        self.key_placed = False
        self.dir_idx = random.randint(0, 3)

    def _get_random_start(self):
        import random
        return (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))

    def run(self, action_callback=None):
        running = True
        clock = pygame.time.Clock()

        while running:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    close_display()
                    return

            if action_callback:
                action = action_callback()
            else:
                keys = pygame.key.get_pressed()
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
                cont = apply_action(self, action)
                if not cont:
                    return

            if not pygame.display.get_init():
                return
            draw_level(self)

if __name__ == "__main__":
    LevelCreator().run()
