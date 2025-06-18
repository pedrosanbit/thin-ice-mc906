import os
import pygame
import torch
import sys
import numpy as np
from src.levels import Level
from src.game import Game
from src.utils import draw_game_screen
from src.env.thin_ice_env import ThinIceEnv
from src.agents.dqn_agent import DQNAgent

pygame.init()

CELL_SIZE = 32
GRID_LENGTH = 19
GRID_HEIGHT = 15
SCREEN_LENGTH = GRID_LENGTH * CELL_SIZE
SCREEN_HEIGHT = (GRID_HEIGHT + 2) * CELL_SIZE

font = pygame.font.SysFont('Cascadia Code', CELL_SIZE)
screen = pygame.display.set_mode((SCREEN_LENGTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gelo Fino - Agente")

WHITE = (218, 240, 255)

# Hiperparâmetros
MAX_STEPS = 400
MAX_ATTEMPTS = 200
SUCCESS_CRIT = 1.0  # sucesso perfeito (todos os blocos de gelo e moedas)

# Inicializa ambiente e agente
env = ThinIceEnv(
    level_folder="original_game",
    level_index=0,
    max_steps=MAX_STEPS,
    render_mode=None,
    seed=42
)

agent = DQNAgent(
    state_shape=env.observation_space.shape,
    n_actions=env.action_space.n,
)

# Loop sobre todas as fases
total_levels = len(os.listdir("data/levels/original_game"))
clock = pygame.time.Clock()

for level_id in range(total_levels):
    env.level_index = level_id
    print(f"\n[🎯 Fase {level_id}] Tentando resolver de forma perfeita...")

    solved_perfectly = False
    attempts = 0

    while not solved_perfectly and attempts < MAX_ATTEMPTS:
        s, info = env.reset()
        done = False
        truncated = False
        attempts += 1
        total_reward = 0

        while not done and not truncated:
            screen.fill(WHITE)

            action = agent.act(s, info["action_mask"])
            s_next, r, done, truncated, info = env.step(action)

            if not info["invalid"]:
                agent.remember(s, action, r, s_next, done or truncated)

            agent.update()
            s = s_next
            total_reward += r

            draw_game_screen(env.game, screen, font)
            pygame.display.flip()
            clock.tick(10)

        if info["result"] == "SUCCESS" and info["score_ratio"] >= SUCCESS_CRIT:
            print(f"[✓] Fase {level_id} resolvida em {attempts} tentativa(s) com perfeição!")
            solved_perfectly = True

    if not solved_perfectly:
        print(f"[x] Fase {level_id} NÃO resolvida perfeitamente após {MAX_ATTEMPTS} tentativas.")

pygame.quit()
sys.exit()
