import pygame
import sys
from levels import get_level
from mapping import get_color
from game import Game

pygame.init()

CELL_SIZE = 32
GRID_LENGTH = 19
GRID_HEIGHT = 15
SCREEN_LENGTH = GRID_LENGTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

screen = pygame.display.set_mode((SCREEN_LENGTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gelo Fino")

WHITE = (255, 255, 255)
PLAYER = (254, 2, 0)

level = get_level(0)
game = Game(0, level.grid, level.start[0], level.start[1], 0, 0, 0)

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(WHITE)
    next_level = game.check_next_level()
    if not next_level: game.check_game_over()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        game.move_player((-1,0))
    if keys[pygame.K_RIGHT]:
        game.move_player((1,0))
    if keys[pygame.K_UP]:
        game.move_player((0,-1))
    if keys[pygame.K_DOWN]:
        game.move_player((0,1))

    for i in range(0, GRID_LENGTH):
        for j in range(0, GRID_HEIGHT):
            x = i * CELL_SIZE
            y = j * CELL_SIZE
            pygame.draw.rect(
                screen,
                get_color(game.grid[j][i]),
                (x, y, CELL_SIZE, CELL_SIZE)
            )

    pygame.draw.rect(
        screen,
        PLAYER,
        (game.player_x * CELL_SIZE, game.player_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )

    pygame.display.flip()
    clock.tick(10)
