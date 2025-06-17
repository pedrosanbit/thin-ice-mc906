# /src/scritps/play.py

import pygame
import sys
from src.levels import Level
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


initial_level = Level(
"original_game",
loop_on_finish=False,
current_level_id=0
)

game = Game(
    level=initial_level,
    perfect_score_required = True,
    points=0,
    current_points=0,
    solved = 0,
    seed=42
)

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(WHITE)
    next_level_state = game.check_progress()

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