# src/scripts/trainer_utils.py

import os
import numpy as np
from src.env.thin_ice_env import ThinIceEnv
from old_level_generator import LevelGenerator
from src.agents.dqn_agent import DQNAgent


def setup_directories():
    os.makedirs("plots", exist_ok=True)
    os.makedirs("models/freitas", exist_ok=True)

def validate_on_original_game(agent, use_action_mask, max_steps=300):
    folder_name = "original_game_augmented"
    path_folder = os.path.join("data/levels/", folder_name)
    files = sorted(
        f for f in os.listdir(path_folder)
        if f.endswith(".txt") and int(f.split("_")[1].split(".")[0]) > 2
    )
    successes = 0
    for i, _ in enumerate(files):
        env = ThinIceEnv(
            level_folder=folder_name,
            level_index=i,
            max_steps=max_steps,
            render_mode=None,
            seed=42,
            allow_failure_progression=True
        )
        s, info = env.reset()
        for _ in range(max_steps):
            a = agent.act(s, info["action_mask"] if use_action_mask else None)
            s, r, done, truncated, info = env.step(a)
            if done or truncated:
                break
        if info["result"] == "SUCCESS":
            successes += 1
    return successes / len(files)

def initialize_environment_and_agent(
    steps_per_episode: int,
    buffer_size: int,
    allow_failure_progression: bool,
    use_action_mask: bool = True
):
    env = ThinIceEnv(
        level_folder="original_game",
        level_index=0,
        max_steps=steps_per_episode,
        render_mode=None,
        seed=42,
        allow_failure_progression=allow_failure_progression
    )

    agent = DQNAgent(
        state_shape=env.observation_space.shape,
        n_actions=env.action_space.n,
        buffer_size=buffer_size
    )
    agent.use_action_mask = use_action_mask  # novo atributo controlado aqui

    model_path = "models/freitas/dqn_agent.pth"
    if os.path.exists(model_path):
        print(f"[✓] Carregando modelo salvo de {model_path}")
        agent.load(model_path)
    else:
        print("[i] Nenhum modelo salvo encontrado. Treinamento começará do zero.")

    return env, agent
