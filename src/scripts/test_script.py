import json
from src.env.thin_ice_env import ThinIceEnv
from src.agents.dqn_agent import DQNAgent

env = ThinIceEnv(
    level_folder="/home/henrique/MC906/thin-ice-mc906/data/levels/original_game", 
    level_index=0, 
    max_steps=300, 
    render_mode=None, 
    seed = 42
)

agent = DQNAgent(
    state_shape=env.observation_space.shape,
    n_actions=env.action_space.n,
)

# Executa a sequência original de níveis
agent.load("models/dqn_agent.pth")

results = []
for idx, level in enumerate("/home/henrique/MC906/thin-ice-mc906/data/levels/original_levels"):
    s, info = env.reset()
    done = False
    truncated = False
    total_reward = 0
    steps = 0

    while not (done or truncated):
        a = agent.act(s, info["action_mask"])
        s, r, done, truncated, info = env.step(a)
        total_reward += r
        steps += 1

    results.append({
        "level_id": idx,
        "result": info["result"],
        "score_ratio": info["score_ratio"],
        "steps": steps
    })
    print(
        f"Level {idx:2d} | Resultado: {info['result']} | Score restante: {1 - info['score_ratio']:.2f} | Passos: {steps}"
    )

# Opcional: salva os resultados em um arquivo
with open("models/test_results.json", "w") as f:
    json.dump(results, f, indent=2)