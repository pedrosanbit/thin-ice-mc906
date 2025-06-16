# /src/main.py

import pygame
import sys
from src.levels import get_level
from src.game import Game
from src.utils import draw_game_screen

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

level_folder = "type_0012_0016"
use_random_levels = False
seed = 42
initial_level = get_level(level_folder, 0)

game = Game(
    num_level=0,
    level=initial_level,
    player_x=initial_level.start[0],
    player_y=initial_level.start[1],
    points=0,
    current_points=0,
    keys_obtained=0,
    current_tiles=0,
    solved=0,
    block_mov=(None, (0, 0)),
    random_levels=use_random_levels,
    seed=seed
)

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(WHITE)
    next_level = game.check_next_level(level_folder)
    if not next_level:
        game.check_game_over(level_folder)

    moving_block, block_direction = game.block_mov
    if moving_block is not None:
        game.move_block(moving_block, block_direction)
    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            game.move_player((-1, 0))
        if keys[pygame.K_RIGHT]:
            game.move_player((1, 0))
        if keys[pygame.K_UP]:
            game.move_player((0, -1))
        if keys[pygame.K_DOWN]:
            game.move_player((0, 1))

    draw_game_screen(game, screen, font)
    
    pygame.display.flip()
    clock.tick(10)