# /src/scripts/train

import matplotlib.pyplot as plt
import numpy as np

from src.env.thin_ice_env import ThinIceEnv
from src.agents.dqn_agent import DQNAgent
from src.levels import build_random_levels

LEVEL_FOLDER = "procedural_generated/type_0012_0016/"

# Gera fases proceduralmente
build_random_levels(
    min_size=12,
    max_size=16,
    total_levels=1000,
    output_folder=LEVEL_FOLDER
)

# Inicializa ambiente e agente
env = ThinIceEnv(level_index=0, level_folder=LEVEL_FOLDER)
agent = DQNAgent(
    state_shape=env.observation_space.shape,
    n_actions=env.action_space.n,
)

success_history = []
tile_ratio_history = []

EPISODES = 2000
STEPS_PER_EP = 300

for ep in range(EPISODES):
    s, info = env.reset()
    total_reward = 0
    solved = False

    for t in range(STEPS_PER_EP):
        a = agent.act(s, info["action_mask"])
        s_next, r, done, truncated, info = env.step(a)

        if not info["invalid"]:
            agent.remember(s, a, r, s_next, done or truncated)

        agent.update()
        s = s_next
        total_reward += r

        if done or truncated:
            solved = done
            break

    if solved:
        total = env.game.level.total_tiles
        feitos = env.game.current_tiles
        print(f"[✓] Episódio {ep}: PASSOU — Tiles restantes: {total - feitos} / {total}")
        success_history.append(1)
        tile_ratio_history.append(feitos / total)
    else:
        print(f"[x] Episódio {ep}: FALHOU")
        success_history.append(0)
        tile_ratio_history.append(0.0)
        
def moving_average(data, window_size=50):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

# Gráfico 1: Sucesso por episódio (média móvel)
plt.figure(figsize=(10, 4))
plt.plot(moving_average(success_history), label='Média móvel (sucesso)', linewidth=2)
plt.title("Taxa de Sucesso por Episódio (média móvel)")
plt.xlabel("Episódio")
plt.ylabel("Taxa de sucesso")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("success_moving_average.png")  # Salva no diretório atual

# Gráfico 2: Porcentagem de tiles pegos
plt.figure(figsize=(10, 4))
plt.plot(tile_ratio_history, label='% Tiles coletados', alpha=0.6)
plt.hlines(np.mean(tile_ratio_history), 0, EPISODES, colors='red', linestyles='dashed', label='Média total')
plt.title("Porcentagem de Tiles Coletados por Episódio")
plt.xlabel("Episódio")
plt.ylabel("Proporção de tiles pegos")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("tile_ratio_per_episode.png")  # Salva no diretório atual