# src/script/train.py
import matplotlib.pyplot as plt
import numpy as np
import json
import os

from src.level_generator import LevelGenerator
from src.env.thin_ice_env import ThinIceEnv
from src.agents.dqn_agent import DQNAgent
from src.level_generator import LevelGenerator

lg_loader = LevelGenerator(
    min_size=4,
    max_size=10
)

niveis = int(input("Quantos níveis deseja gerar? "))
LEVEL_FOLDER = lg_loader.build_random_levels(niveis)

env = ThinIceEnv(
    level_folder=LEVEL_FOLDER, 
    level_index=0, 
    max_steps=300, 
    render_mode=None, 
    seed = 42
)

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
            solved = (info["result"] == "SUCCESS")
            break

    if solved:
        total = env.game.level.total_tiles
        feitos = env.game.current_tiles
        print(
            f"[✓] Episódio {ep:4d} | Status: PASSOU  | Nível: {info['level_id']:4d} "
            f"| Score restante: {1 - info['score_ratio']:.2f} | Resultado: {info['result']}"
        )
        success_history.append(1)
        tile_ratio_history.append(feitos / total)
        if (info['level_id'] == niveis-1):
            print("Treinamento concluído com sucesso!")
            break
    else:
        print(
            f"[x] Episódio {ep:4d} | Status: FALHOU  | Nível: {info['level_id']:4d} "
            f"| Score restante: {1 - info['score_ratio']:.2f} | Resultado: {info['result']}"
        )
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

# Salva o modelo treinado

os.makedirs("models", exist_ok=True)
agent.save("models/dqn_agent.pth")