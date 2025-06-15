# src/util.py

import pygame
from src.mapping import Map, get_color
from src.game import Game

def init_screen():
    pygame.init()
    CELL_SIZE = 32
    GRID_LENGTH = 19
    GRID_HEIGHT = 15
    SCREEN_LENGTH = GRID_LENGTH * CELL_SIZE
    SCREEN_HEIGHT = (GRID_HEIGHT + 2) * CELL_SIZE

    screen = pygame.display.set_mode((SCREEN_LENGTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont('Cascadia Code', CELL_SIZE)
    
    return screen, font


def draw_game_screen(game, screen, font):
    CELL_SIZE = 32
    GRID_LENGTH = 19
    GRID_HEIGHT = 15
    SCREEN_HEIGHT = (GRID_HEIGHT + 2) * CELL_SIZE

    WHITE = (218, 240, 255)
    PLAYER = (254, 2, 0)
    TEXT = (0, 78, 158)

    screen.fill(WHITE)

    # HUD
    level_text = font.render(f'LEVEL {game.num_level + 1}', True, TEXT)
    progress_text = font.render(f'{game.current_tiles} / {game.level.total_tiles}', True, TEXT)
    solved_text = font.render(f'SOLVED {game.solved}', True, TEXT)
    points_text = font.render(f'POINTS {game.current_points}', True, TEXT)

    screen.blit(level_text, (54, 4))
    screen.blit(progress_text, (257, 4))
    screen.blit(solved_text, (437, 4))
    screen.blit(points_text, (438, SCREEN_HEIGHT - CELL_SIZE + 4))

    # Grid
    for i in range(GRID_LENGTH):
        for j in range(GRID_HEIGHT):
            x = i * CELL_SIZE
            y = (j + 1) * CELL_SIZE
            pygame.draw.rect(
                screen,
                get_color(game.level.grid[j][i]),
                (x, y, CELL_SIZE, CELL_SIZE)
            )

    # Moedas
    for coin_bag in game.level.coin_bags:
        x = coin_bag[0] * CELL_SIZE
        y = (coin_bag[1] + 1) * CELL_SIZE
        pygame.draw.circle(
            screen,
            get_color(Map.COIN_BAG.value),
            (x + CELL_SIZE / 2, y + CELL_SIZE / 2),
            CELL_SIZE * 3 / 8
        )

    # Chaves
    for key in game.level.keys:
        x = key[0] * CELL_SIZE
        y = (key[1] + 1) * CELL_SIZE
        pygame.draw.circle(
            screen,
            get_color(Map.LOCK.value),
            (x + CELL_SIZE / 2, y + CELL_SIZE / 2),
            CELL_SIZE * 3 / 8
        )

    # Blocos
    for block in game.level.blocks:
        x = block[0] * CELL_SIZE
        y = (block[1] + 1) * CELL_SIZE
        pygame.draw.rect(
            screen,
            get_color(Map.BLOCK.value),
            (x, y, CELL_SIZE, CELL_SIZE)
        )

    # Jogador
    pygame.draw.rect(
        screen,
        PLAYER,
        (game.player_x * CELL_SIZE, (game.player_y + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )