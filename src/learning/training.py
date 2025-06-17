import os
from sb3_contrib import MaskablePPO
from src.learning.thin_ice_env import ThinIceEnv

SAVE_PATH = "models"

print("Starting training...")
env = ThinIceEnv()
model = MaskablePPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=1_000_000)
model.save(os.path.join(SAVE_PATH, "ppo_thin_ice"))
print("Training finished!")