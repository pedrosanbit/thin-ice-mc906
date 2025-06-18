# src/scripts/validate.py

import pygame
import os
from src.utils import init_screen, draw_game_screen
from src.level_generator import LevelGenerator
from src.env.thin_ice_env import ThinIceEnv
from src.agents.dqn_agent import DQNAgent

# ⚙️ Configuração
STEPS_PER_EP = 400
NUM_LEVELS = 36
LEVEL_FOLDER = "original_game"

# Inicializa pygame
screen, font = init_screen()
clock = pygame.time.Clock()


# Carrega ambiente e agente
env = ThinIceEnv(
    level_folder=LEVEL_FOLDER,
    level_index=0,
    max_steps=STEPS_PER_EP,
    render_mode=None,
    seed=42
)

agent = DQNAgent(
    state_shape=env.observation_space.shape,
    n_actions=env.action_space.n,
)

model_path = "models/freitas/dqn_agent.pth"
assert os.path.exists(model_path), f"Modelo não encontrado em {model_path}"
agent.load(model_path)
print(f"[✓] Modelo carregado de {model_path}")

# 🎮 Execução do agente nas fases de validação
for level_idx in range(NUM_LEVELS):
    print(f"\n=== Fase {level_idx} ===")
    env.level_index = level_idx
    s, info = env.reset()
    total_reward = 0

    for step in range(STEPS_PER_EP):
        a = agent.act(s, info["action_mask"])
        s_next, r, done, truncated, info = env.step(a)

        draw_game_screen(env.game, screen, font)
        pygame.display.flip()
        clock.tick(10)  # 10 FPS

        s = s_next
        total_reward += r

        if done or truncated:
            break

    print(f"Resultado: {info['result']} | Score: {total_reward:.2f} | Tiles: {(1 - info['score_ratio']):.2f}")

pygame.quit()
