# src/scripts/try_solve.py
import numpy as np
from pathlib import Path
from src.env.thin_ice_env import ThinIceEnv
from src.agents.dqn_agent import DQNAgent

MODEL_PATH   = Path("models/freitas/dqn_agent_22.pth")
LEVEL_FOLDER = "original_game"      # ou a pasta que quiser testar
MAX_STEPS    = 300                  # igual ao treino

def main():
    # ambiente zerado
    env   = ThinIceEnv(level_index=0, level_folder=LEVEL_FOLDER)
    agent = DQNAgent(
        state_shape=env.observation_space.shape,
        n_actions=env.action_space.n,
    )
    agent.load(MODEL_PATH)
    agent.epsilon = 0.0             # greedy puro – sem exploração

    total_levels   = 0
    solved_levels  = 0
    tile_ratios    = []

    while True:
        obs, info = env.reset()
        total_levels += 1
        solved = False

        for _ in range(MAX_STEPS):
            action = agent.act(obs, info["action_mask"])
            obs, reward, done, truncated, info = env.step(action)
            if done or truncated:
                solved = done
                break

        # estatística da fase
        if solved:
            total   = env.game.level.total_tiles
            feitos  = env.game.current_tiles
            tile_ratios.append(feitos / total)
            solved_levels += 1
            print(f"[✓] Fase {total_levels:03d} resolvida – {feitos}/{total} tiles")
        else:
            tile_ratios.append(0.0)
            print(f"[x] Fase {total_levels:03d} falhou")

        # quebra quando acabar o lote de fases
        if not env.game.check_next_level(LEVEL_FOLDER):
            break

    # resumo
    print("\n===== RESUMO =====")
    print(f"Total de fases testadas : {total_levels}")
    print(f"Fases resolvidas        : {solved_levels}")
    if total_levels:
        print(f"Taxa de sucesso         : {solved_levels/total_levels:.1%}")
        print(f"Média de tiles derretidos: {np.mean(tile_ratios):.2%}")

if __name__ == "__main__":
    main()
