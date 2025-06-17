import numpy as np
from itertools import product
from sb3_contrib import MaskablePPO
from src.learning.thin_ice_env import ThinIceEnv

def evaluate_model(model, env, steps, num_episodes=10, render=False):
    """
    Evaluate a trained RL model in the environment.
    
    Args:
        model: The trained RL model (e.g., MaskablePPO).
        env: The environment to evaluate the model in.
        num_episodes: Number of episodes to run for evaluation.
        render: Whether to render the environment during evaluation (default: False).
    
    Returns:
        float: The average reward over the evaluated episodes.
        list: A list of rewards obtained in each episode.
    """
    total_rewards = []
    
    for episode in range(num_episodes):
        obs, _ = env.reset()  # Reset the environment at the start of each episode
        done = False
        episode_reward = 0
        current_steps = 0
        
        while not done and current_steps <= steps:
            # Predict action using the trained model
            action_masks = env.action_masks()  # Get action masks if applicable
            action, _states = model.predict(obs, action_masks=action_masks)
            
            # Take the action in the environment
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # Accumulate rewards
            episode_reward += reward
            current_steps += 1
        
        total_rewards.append(episode_reward)
        print(f"Episode {episode + 1}: Reward = {episode_reward}")
    
    # Calculate the average reward over all episodes
    avg_reward = np.mean(total_rewards)
    print(f"Average Reward over {num_episodes} episodes: {avg_reward}")
    
    return avg_reward, total_rewards

env = ThinIceEnv()

learning_rates = [1e-3, 1e-4, 1e-5]
batch_sizes = [64, 128, 256]
n_steps = [2048, 4096, 8192]

for lr, bs, steps in product(learning_rates, batch_sizes, n_steps):
    model = MaskablePPO("MlpPolicy", env, learning_rate=lr, batch_size=bs, n_steps=steps, verbose=1)
    model.learn(total_timesteps=100_000)
    avg_reward, total_rewards = evaluate_model(model, env, steps)  # Função para calcular a recompensa média em episódios de teste
    print(f"lr={lr}, bs={bs}, steps={steps}, avg_reward={avg_reward}, total_rewards={total_rewards}")