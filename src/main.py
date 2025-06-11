import pygame
import sys
import os
from src.mapping import Map, get_color
from stable_baselines3 import PPO
from src.learning.thin_ice_env import ThinIceEnv

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

clock = pygame.time.Clock()

env = ThinIceEnv()
model = PPO.load(os.path.join('models', 'ppo_thin_ice'), env)

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

    action, _states = model.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated

    screen.fill(WHITE)

    level_text =  font.render(f'LEVEL {env.game.num_level + 1}', True, TEXT)
    progress_text = font.render(f'{env.game.current_tiles} / {env.game.level.total_tiles}', True, TEXT)
    solved_text = font.render(f'SOLVED {env.game.solved}', True, TEXT)
    points_text = font.render(f'POINTS {env.game.current_points}', True, TEXT)

    screen.blit(level_text, (54, 4))
    screen.blit(progress_text, (257, 4))
    screen.blit(solved_text, (437, 4))
    screen.blit(points_text, (438, SCREEN_HEIGHT - CELL_SIZE + 4))

    for i in range(0, GRID_LENGTH):
        for j in range(0, GRID_HEIGHT):
            x = i * CELL_SIZE
            y = (j + 1) * CELL_SIZE
            pygame.draw.rect(
                screen,
                get_color(env.game.level.grid[j][i]),
                (x, y, CELL_SIZE, CELL_SIZE)
            )

    for coin_bag in env.game.level.coin_bags:
        x = coin_bag[0] * CELL_SIZE
        y = (coin_bag[1] + 1) * CELL_SIZE
        pygame.draw.circle(
            screen, 
            get_color(Map.COIN_BAG.value), 
            (x + CELL_SIZE / 2, y + CELL_SIZE / 2), 
            CELL_SIZE * 3/8
        )

    for key in env.game.level.keys:
        x = key[0] * CELL_SIZE
        y = (key[1] + 1) * CELL_SIZE
        pygame.draw.circle(
            screen, 
            get_color(Map.LOCK.value), 
            (x + CELL_SIZE / 2, y + CELL_SIZE / 2), 
            CELL_SIZE * 3/8
        )

    for block in env.game.level.blocks:
        x = block[0] * CELL_SIZE
        y = (block[1] + 1) * CELL_SIZE
        pygame.draw.rect(
            screen, 
            get_color(Map.BLOCK.value), 
            (x, y, CELL_SIZE, CELL_SIZE)
        )

    pygame.draw.rect(
        screen,
        PLAYER,
        (env.game.player_x * CELL_SIZE, (env.game.player_y + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )

    pygame.display.flip()
    clock.tick(10)
