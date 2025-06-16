# src/script/train.py
import matplotlib.pyplot as plt
import numpy as np

from src.level_generator import LevelGenerator
from src.env.thin_ice_env import ThinIceEnv
from src.agents.dqn_agent import DQNAgent

# --------------------------------------------------
# 1. Conjunto de fases
# --------------------------------------------------
lg = LevelGenerator(min_size=12, max_size=16)
level_set = lg.build_random_levels(total_levels=1000)   # devolve LevelSet

# --------------------------------------------------
# 2. Ambiente e agente
# --------------------------------------------------
env = ThinIceEnv(
    level_set   = level_set,   # <-- passa o próprio LevelSet
    start_index = 0,           # nível inicial
    max_steps   = 300,         # (opcional) igual ao STEPS_PER_EP
)

agent = DQNAgent(
    state_shape = env.observation_space.shape,
    n_actions   = env.action_space.n,
)

# --------------------------------------------------
# 3. Loop de treinamento
# --------------------------------------------------
success_history, tile_ratio_history = [], []
success_history, ratio_history = [], []
EPISODES      = 2000
STEPS_PER_EP  = 300

for ep in range(EPISODES):
    s, info = env.reset()
    total_reward = 0.0

    for _ in range(STEPS_PER_EP):
        a = agent.act(s, info["action_mask"])
        s_next, r, done, truncated, info = env.step(a)

        if not info["invalid"]:
            agent.remember(s, a, r, s_next, done or truncated)

        agent.update()
        s           = s_next
        total_reward += r

        if done or truncated:
            break

    if info["advanced"]:                         # passou de fase
        ratio = info["points_ratio"]
        print(f"[✓] Episódio {ep}: PASSOU — Pontos coletados: {ratio:.2%}")
        success_history.append(1)
        ratio_history.append(ratio)
    else:
        print(f"[x] Episódio {ep}: FALHOU")
        success_history.append(0)
        ratio_history.append(0.0)

import matplotlib.pyplot as plt

def moving_average(data, window_size=50):
    if len(data) < window_size:
        return data  # evita array vazio no início
    return np.convolve(data, np.ones(window_size) / window_size, mode="valid")

# 4.1 – Taxa de sucesso (média móvel)
plt.figure(figsize=(10, 4))
plt.plot(moving_average(success_history), linewidth=2, label="Média móvel (sucesso)")
plt.title("Taxa de Sucesso por Episódio")
plt.xlabel("Episódio")
plt.ylabel("Sucesso (0–1)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("success_moving_average.png")
plt.close()

# 4.2 – Razão de pontos coletados
plt.figure(figsize=(10, 4))
episodes = np.arange(len(ratio_history))
plt.plot(episodes, ratio_history, alpha=0.4, label="Pontuação episódio a episódio")
plt.plot(
    episodes[len(episodes) - len(moving_average(ratio_history)) :],
    moving_average(ratio_history),
    linewidth=2,
    label="Média móvel (pontos)",
)
plt.hlines(
    np.mean(ratio_history),
    0,
    episodes[-1],
    colors="red",
    linestyles="dashed",
    label=f"Média total ({np.mean(ratio_history):.2%})",
)
plt.title("Razão de Pontos Coletados por Episódio")
plt.xlabel("Episódio")
plt.ylabel("Proporção de pontos (0–1)")
plt.ylim(0, 1.05)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("points_ratio_per_episode.png")
plt.close()

# 4.3 – (Opcional) Histograma das razões
plt.figure(figsize=(6, 4))
plt.hist(ratio_history, bins=20, alpha=0.7, edgecolor="black")
plt.title("Distribuição da Razão de Pontos Coletados")
plt.xlabel("Proporção de pontos (0–1)")
plt.ylabel("Frequência")
plt.tight_layout()
plt.savefig("points_ratio_hist.png")
plt.close()