
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_batch_summary(results: list[str], mean_steps: float, round_id: int, save_dir: str = "plots"):
    os.makedirs(save_dir, exist_ok=True)

    # Conta os tipos de resultado
    total = len(results)
    success = results.count("SUCCESS") / total
    not_sufficient = results.count("NOT_SUFFICIENT") / total
    game_over = results.count("GAME_OVER") / total

    # Gráfico de barras para proporções
    plt.figure(figsize=(8, 4))
    plt.bar(["SUCCESS", "NOT_SUFFICIENT", "GAME_OVER"],
            [success, not_sufficient, game_over],
            color=["green", "orange", "red"])
    plt.title(f"Distribuição de Resultados - Round {round_id} (µ={int(mean_steps)})")
    plt.ylim(0, 1)
    plt.ylabel("Proporção")
    plt.tight_layout()
    plt.savefig(f"{save_dir}/round_{round_id:02d}_result_distribution.png")
    plt.close()

    # Salva a média de passos (caso queira plottar depois externamente)
    with open(f"{save_dir}/mean_steps_log.txt", "a") as f:
        f.write(f"{round_id},{mean_steps:.2f}\n")


import matplotlib.pyplot as plt
import numpy as np
import json
import os

import shutil
import random

import pygame
from src.utils import init_screen, draw_game_screen
from src.level_generator import LevelGenerator
from src.env.thin_ice_env import ThinIceEnv
from src.agents.dqn_agent import DQNAgent


EPISODES_PER_ROUND = 300
STEPS_PER_EP = 400
INITIAL_MEAN = 4
STD_RATIO = 0.2
MAX_MEAN = 250
WINDOW_SIZE = 500
GROWTH = 1.05
SUCCESS_THRESHOLD = 0.93

USE_PYGAME = False

if USE_PYGAME:
    screen, font = init_screen()
    clock = pygame.time.Clock()


mean_steps = INITIAL_MEAN
success_history = []
tile_ratio_history = []

# Inicializa ambiente e agente
env = ThinIceEnv(
    level_folder="original_game",
    level_index=0,
    max_steps=STEPS_PER_EP,
    render_mode=None,
    seed=42
)

agent = DQNAgent(
    state_shape=env.observation_space.shape,
    n_actions=env.action_space.n,
)

model_path = "dqn_agent_04.4.pth"
if os.path.exists(model_path):
    print(f"[✓] Carregando modelo salvo de {model_path}")
    agent.load(model_path)
else:
    print("[i] Nenhum modelo salvo encontrado. Treinamento começará do zero.")


# ------------------ Loop de Curriculum Adaptativo ------------------
for curriculum_round in range(2000):
    print(f"\n[Currículo {curriculum_round}] Gerando fases com média ~{int(mean_steps)}")
    lg = LevelGenerator(mean_steps=int(mean_steps), std_ratio=STD_RATIO)
    level_dir = lg.build_random_levels(EPISODES_PER_ROUND)
    env.change_level_folder(level_dir)
    env.level_index = 0

    batch_results =[]

    for ep in range(EPISODES_PER_ROUND):
        s, info = env.reset()
        total_reward = 0
        solved = False

        for t in range(STEPS_PER_EP):
            a = agent.act(s, info["action_mask"])
            s_next, r, done, truncated, info = env.step(a)

            if USE_PYGAME:
                draw_game_screen(env.game, screen, font)
                pygame.display.flip()
                clock.tick(10)

            if not info["invalid"]:
                agent.remember(s, a, r, s_next, done or truncated)

            agent.update()
            s = s_next
            total_reward += r

            if done or truncated:
                solved = (info["result"] == "SUCCESS")
                break

        batch_results.append(info["result"])

        if solved:
            total = env.game.level.total_tiles
            feitos = env.game.current_tiles
            print(f"[✓] Ep {ep:4d} | µ={int(mean_steps):3d} | Tiles: {1 - info['score_ratio']:.2f} | Resultado: {info['result']}")
            success_history.append(1)
            tile_ratio_history.append(feitos / total)
        else:
            print(f"[x] Ep {ep:4d} | µ={int(mean_steps):3d} | Tiles: {1 - info['score_ratio']:.2f} | Resultado: {info['result']}")
            success_history.append(0)
            tile_ratio_history.append(0.0)


    plot_batch_summary(batch_results, mean_steps, curriculum_round)

    # Avaliação e progressão do currículo
    recent_success = np.mean(success_history[-WINDOW_SIZE:])
    print(f"[Currículo {curriculum_round}] Sucesso nos últimos {WINDOW_SIZE}: {recent_success:.2f}")

    if recent_success > SUCCESS_THRESHOLD and mean_steps < MAX_MEAN:
        mean_steps = min(mean_steps * GROWTH, MAX_MEAN)
        print(f"↑ Aumentando mean_steps para {int(mean_steps)}")
    elif recent_success < 0.3 and mean_steps > INITIAL_MEAN:
        mean_steps = max(mean_steps * 0.9, INITIAL_MEAN)
        print(f"↓ Reduzindo mean_steps para {int(mean_steps)}")

    if mean_steps >= MAX_MEAN:
        print("🎯 Curriculum finalizado com sucesso!")
        break

    # Salva o modelo após cada rodada de currículo
    os.makedirs("models", exist_ok=True)
    model_path = f"models/freitas/dqn_agent_{int(mean_steps)}.pth"
    agent.save(model_path)
    print(f"[✓] Modelo salvo em {model_path}")


# ------------------ Gráficos ------------------
def moving_average(data, window=50):
    return np.convolve(data, np.ones(window) / window, mode="valid")

plt.figure(figsize=(10, 4))
plt.plot(moving_average(success_history), label="Média móvel (sucesso)", linewidth=2)
plt.title("Taxa de Sucesso por Episódio")
plt.xlabel("Episódio")
plt.ylabel("Taxa de sucesso")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("success_moving_average.png")

plt.figure(figsize=(10, 4))
plt.plot(tile_ratio_history, label="% Tiles coletados", alpha=0.6)
plt.hlines(np.mean(tile_ratio_history), 0, len(tile_ratio_history), colors='red', linestyles='dashed', label="Média total")
plt.title("Porcentagem de Tiles Coletados por Episódio")
plt.xlabel("Episódio")
plt.ylabel("Proporção")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("tile_ratio_per_episode.png")

if USE_PYGAME:
    pygame.quit()