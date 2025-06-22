### src/level_generator/drawing.py
import pygame
from src.mapping import *


def close_display():
    pygame.display.quit()
    

def draw_level(creator):
    creator.screen.fill((218, 240, 255))

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(
                creator.screen,
                get_color(creator.grid[y][x]),
                (x * CELL_SIZE, (y + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )

    for cx, cy in creator.coin_bags:
        pygame.draw.circle(creator.screen, get_color(creator.Map.COIN_BAG.value),
                           (cx * CELL_SIZE + CELL_SIZE // 2, (cy + 1) * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 3)

    for kx, ky in creator.keys:
        pygame.draw.circle(creator.screen, get_color(creator.Map.LOCK.value),
                           (kx * CELL_SIZE + CELL_SIZE // 2, (ky + 1) * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 3)

    for tx, ty in creator.teleports:
        pygame.draw.circle(creator.screen, (200, 0, 255),
                           (tx * CELL_SIZE + CELL_SIZE // 2, (ty + 1) * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 3)

    pygame.draw.rect(creator.screen, (255, 0, 0),
                     (creator.player_x * CELL_SIZE, (creator.player_y + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    pygame.display.flip()
