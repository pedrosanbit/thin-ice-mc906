# src/main.py (exemplo sem função legada)

import sys
import pygame

from src.level_set import LevelSet, Progression
from src.game import Game, Mode
from src.utils import draw_game_screen

# Configurações
LEVEL_FOLDER = "type_0012_0016"
MAX_INDEX = 999             # maior ID disponível nesse diretório
PROGRESSION = Progression.SEQUENTIAL   # ou Progression.RANDOM
MODE = Mode.NORMAL                         # ou Mode.RESTRICTED
CELL_SIZE = 32
GRID_W, GRID_H = 19, 15
WHITE = (218, 240, 255)

# Inicia pygame
pygame.init()
font = pygame.font.SysFont("Cascadia Code", CELL_SIZE)
screen = pygame.display.set_mode((GRID_W * CELL_SIZE, (GRID_H + 2) * CELL_SIZE))
pygame.display.set_caption("Gelo Fino (Refatorado)")
clock = pygame.time.Clock()

# Cria LevelSet e Game
level_set = LevelSet(LEVEL_FOLDER, MAX_INDEX, progression=PROGRESSION)

game = Game(level_set=level_set, mode=MODE, start_index=0)

# Loop principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(WHITE)

    avancou, ratio = game.check_finish()
    if not avancou:
        game.check_game_over()

    if ratio > 0:  # feedback no modo RESTRICTED
        print(f"[INFO] reiniciou — perdeu {ratio*100:.1f}% dos pontos")

    moving_block, block_dir = game.block_mov
    if moving_block is not None:
        game.move_block(moving_block, block_dir)
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