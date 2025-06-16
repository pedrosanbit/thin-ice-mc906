# src/utils.py

import pygame
from src.mapping import Map, get_color
from src.game import Game

CELL_SIZE = 32
GRID_LENGTH = 19
GRID_HEIGHT = 15
SCREEN_LENGTH = GRID_LENGTH * CELL_SIZE
SCREEN_HEIGHT = (GRID_HEIGHT + 2) * CELL_SIZE

def init_screen():
    """Inicialização da janela do jogo"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_LENGTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont("Cascadia Code", CELL_SIZE)
    return screen, font



def draw_game_screen(game: Game, screen: pygame.Surface, font: pygame.font.Font) -> None:
    """Desenha HUD + grid. Usa :class:`Grid` para acesso seguro."""

    WHITE = (218, 240, 255)
    PLAYER = (254, 2, 0)
    TEXT = (0, 78, 158)

    screen.fill(WHITE)

    # ------------- HUD -------------
    level_text = font.render(f"LEVEL {game.num_level + 1}", True, TEXT)
    progress_text = font.render(
        f"{game.current_tiles} / {game.level.total_tiles}", True, TEXT
    )
    solved_text = font.render(f"SOLVED {game.solved}", True, TEXT)
    points_text = font.render(f"POINTS {game.current_points}", True, TEXT)

    screen.blit(level_text, (54, 4))
    screen.blit(progress_text, (257, 4))
    screen.blit(solved_text, (437, 4))
    screen.blit(points_text, (438, SCREEN_HEIGHT - CELL_SIZE + 4))

    # ------------- Grid -------------
    g = game.level.grid  # conveniência
    for y in range(g.height):
        for x in range(g.width):
            tile = g.tile(x, y)
            pygame.draw.rect(
                screen,
                get_color(tile.value),  # get_color ainda espera int
                (x * CELL_SIZE, (y + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )

    # ------------- Itens móveis -------------
    def _cell_center(cx: int, cy: int):
        return (
            cx * CELL_SIZE + CELL_SIZE // 2,
            (cy + 1) * CELL_SIZE + CELL_SIZE // 2,
        )

    # Moedas
    for cb in game.level.coin_bags:
        pygame.draw.circle(
            screen,
            get_color(Map.COIN_BAG.value),
            _cell_center(*cb),
            int(CELL_SIZE * 0.375),
        )

    # Chaves
    for key in game.level.keys:
        pygame.draw.circle(
            screen,
            get_color(Map.LOCK.value),
            _cell_center(*key),
            int(CELL_SIZE * 0.375),
        )

    # Blocos
    for bx, by in game.level.blocks:
        pygame.draw.rect(
            screen,
            get_color(Map.BLOCK.value),
            (bx * CELL_SIZE, (by + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        )

    # Jogador
    pygame.draw.rect(
        screen,
        PLAYER,
        (
            game.player_x * CELL_SIZE,
            (game.player_y + 1) * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        ),
    )

    # Atualiza display
    pygame.display.flip()
