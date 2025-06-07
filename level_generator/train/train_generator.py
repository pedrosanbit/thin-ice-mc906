# train_generator

import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.env_util import make_vec_env
from gymnasium import Env
from level_generator.rl_envs.thinice_env import ThinIcePhaseGenEnv

SAVE_PATH = "models/generator_ppo"
GENERATED_LEVELS_DIR = "data/levels/procedural_generated"

os.makedirs(SAVE_PATH, exist_ok=True)
os.makedirs(GENERATED_LEVELS_DIR, exist_ok=True)

# Wrap environment
env = DummyVecEnv([lambda: ThinIcePhaseGenEnv()])

# Instantiate model
model = PPO("MultiInputPolicy", env, verbose=1)

# Train the agent
model.learn(total_timesteps=1_000_000)

# Save model
model.save(os.path.join(SAVE_PATH, "ppo_thinice"))

# Reload model (optional)
# model = PPO.load(os.path.join(SAVE_PATH, "ppo_thinice"))

# Generate and save 100 levels
env = ThinIcePhaseGenEnv()
for i in range(100):
    obs, _ = env.reset()  # Corrigido aqui
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, done, _, _ = env.step(action)  # Corrigido aqui também
    env.save_level(os.path.join(GENERATED_LEVELS_DIR, f"generated_{i:03d}"))
