# /src/main.py

import pygame
import sys
from src.levels import get_level
from src.game import Game
from src.utils import draw_game_screen
from src.learning.thin_ice_env import ThinIceEnv
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks
import os

pygame.init()

CELL_SIZE = 32
GRID_LENGTH = 19
GRID_HEIGHT = 15
SCREEN_LENGTH = GRID_LENGTH  * CELL_SIZE
SCREEN_HEIGHT = (GRID_HEIGHT + 2) * CELL_SIZE

font = pygame.font.SysFont('Cascadia Code', CELL_SIZE)
screen = pygame.display.set_mode((SCREEN_LENGTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gelo Fino")

WHITE = (218, 240, 255)
PLAYER = (254, 2, 0)
TEXT = (0, 78, 158)

level_folder = "original_game"
use_random_levels = False
seed = 42
initial_level = get_level(level_folder, 0)

clock = pygame.time.Clock()

env = ThinIceEnv()
model = MaskablePPO.load(os.path.join('models', 'ppo_thin_ice'), env)

obs, _ = env.reset()
done = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if done:
        pygame.quit()
        sys.exit()

    action_masks = get_action_masks(env)
    action, _states = model.predict(obs, action_masks=action_masks)
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated

    screen.fill(WHITE)

    draw_game_screen(env.game, screen, font)
    
    pygame.display.flip()
    clock.tick(10)
    
