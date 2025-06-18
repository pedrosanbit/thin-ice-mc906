import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from src.env.thin_ice_env import ThinIceEnv
from src.level_generator import LevelGenerator
from src.agents.dqn_agent import DQNAgent
from src.utils import draw_game_screen, init_screen
import pygame


# ------------------ Hiperparâmetros e Configuração ------------------

EPISODES_PER_ROUND = 400
STEPS_PER_EP = 400
INITIAL_MEAN = 6
STD_RATIO = 0.5
MAX_MEAN = 160
WINDOW_SIZE = 100
GROWTH = 1.5
SUCCESS_THRESHOLD = 0.85
BUFFER_SIZE = 50_000
UPDATE_FREQ = 4
MIN_BUFFER_SIZE = 1000

USE_VALIDATION = False
USE_PYGAME = False
ALLOW_FAILURE_PROGRESSION = False


# ------------------ Utilitários ------------------

def setup_directories():
    os.makedirs("plots", exist_ok=True)
    os.makedirs("models/freitas", exist_ok=True)


def initialize_environment_and_agent():
    env = ThinIceEnv(
        level_folder="original_game",
        level_index=0,
        max_steps=STEPS_PER_EP,
        render_mode=None,
        seed=42,
        allow_failure_progression=ALLOW_FAILURE_PROGRESSION
    )

    agent = DQNAgent(
        state_shape=env.observation_space.shape,
        n_actions=env.action_space.n,
        buffer_size=BUFFER_SIZE
    )

    model_path = "models/freitas/dqn_agent.pth"
    if os.path.exists(model_path):
        print(f"[✓] Carregando modelo salvo de {model_path}")
        agent.load(model_path)
    else:
        print("[i] Nenhum modelo salvo encontrado. Treinamento começará do zero.")
    
    return env, agent


def run_episode(env, agent):
    s, info = env.reset()
    total_reward, solved = 0, False

    for t in range(STEPS_PER_EP):
        a = agent.act(s, info["action_mask"])
        s_next, r, done, truncated, info = env.step(a)

        if not info["invalid"]:
            agent.remember(s, a, r, s_next, done or truncated)

        if len(agent.buffer) > MIN_BUFFER_SIZE and t % UPDATE_FREQ == 0:
            agent.update()

        s = s_next
        total_reward += r

        if done or truncated:
            solved = info["result"] == "SUCCESS"
            break

    return info, solved


def validate_on_original_game(agent, max_steps=300) -> float:
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
            a = agent.act(s, info["action_mask"])
            s, r, done, truncated, info = env.step(a)
            if done or truncated:
                break
        if info["result"] == "SUCCESS":
            successes += 1

    return successes / len(files)


def plot_batch_summary(results, mean_steps, round_id, val_success_ratio, save_dir="plots"):
    os.makedirs(save_dir, exist_ok=True)
    total = len(results)
    success = results.count("SUCCESS") / total
    not_sufficient = results.count("NOT_SUFFICIENT") / total
    game_over = results.count("GAME_OVER") / total

    plt.figure(figsize=(8, 4))
    labels = ["SUCCESS", "NOT_SUFFICIENT", "GAME_OVER", "VALIDAÇÃO"]
    values = [success, not_sufficient, game_over, val_success_ratio]
    colors = ["green", "orange", "red", "blue"]

    plt.bar(labels, values, color=colors)
    plt.title(f"Distribuição de Resultados - Round {round_id} (µ={int(mean_steps)})")
    plt.ylim(0, 1)
    plt.ylabel("Proporção")
    plt.tight_layout()
    plt.savefig(f"{save_dir}/round_{round_id:02d}_result_distribution.png")
    plt.close()

    with open(f"{save_dir}/mean_steps_log.txt", "a") as f:
        f.write(f"{round_id},{mean_steps:.2f}\n")


def save_round_summary_csv(round_id, batch_results, val_success_ratio, save_path="round_summary.csv"):
    success = batch_results.count("SUCCESS")
    not_sufficient = batch_results.count("NOT_SUFFICIENT")
    game_over = batch_results.count("GAME_OVER")
    total = len(batch_results)

    file_exists = os.path.exists(save_path)
    with open(save_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["round", "success", "not_sufficient", "game_over", "total", "val_success_ratio"])
        writer.writerow([round_id, success, not_sufficient, game_over, total, val_success_ratio])


def curriculum_loop(env, agent):
    mean_steps = INITIAL_MEAN
    success_history = []
    tile_ratio_history = []

    for round_id in range(200_000):
        lg = LevelGenerator(mean_steps=int(mean_steps), std_steps=STD_RATIO)
        level_dir = lg.build_random_levels(EPISODES_PER_ROUND, extra_levels=100)

        env.change_level_folder(level_dir)

        batch_results = []
        for ep in range(EPISODES_PER_ROUND):
            info, solved = run_episode(env, agent)
            batch_results.append(info["result"])
            success_history.append(int(solved))
            tile_ratio_history.append(env.game.current_tiles / env.game.level.total_tiles if solved else 0.0)

        val_ratio = validate_on_original_game(agent) if USE_VALIDATION else 0.0

        success_rate = batch_results.count("SUCCESS") / EPISODES_PER_ROUND
        not_sufficient_rate = batch_results.count("NOT_SUFFICIENT") / EPISODES_PER_ROUND
        game_over_rate = batch_results.count("GAME_OVER") / EPISODES_PER_ROUND

        print(
            f"[✓] Round {round_id} | µ={int(mean_steps)} | "
            f"Treino: SUCCESS={success_rate:.2%}, NOT_SUFFICIENT={not_sufficient_rate:.2%}, GAME_OVER={game_over_rate:.2%} | "
            f"Validação: {val_ratio:.2f} | Últimos {WINDOW_SIZE}: {np.mean(success_history[-WINDOW_SIZE:]):.2f}"
        )

        plot_batch_summary(batch_results, mean_steps, round_id, val_ratio)
        save_round_summary_csv(round_id, batch_results, val_ratio)

        recent_success = np.mean(success_history[-WINDOW_SIZE:])
        if recent_success > SUCCESS_THRESHOLD and mean_steps < MAX_MEAN:
            mean_steps = min(int(mean_steps * GROWTH), MAX_MEAN)
            print(f"↑ Aumentando mean_steps para {int(mean_steps)}")
        elif recent_success < 0.3 and mean_steps > INITIAL_MEAN:
            mean_steps = max(int(mean_steps * 0.9), INITIAL_MEAN)
            print(f"↓ Reduzindo mean_steps para {int(mean_steps)}")

        model_path = f"models/freitas/dqn_agent_{int(mean_steps)}.pth"
        agent.save(model_path)

        if mean_steps >= MAX_MEAN:
            print("🎯 Curriculum finalizado com sucesso!")
            break


def main():
    setup_directories()
    if USE_PYGAME:
        screen, font = init_screen()
    env, agent = initialize_environment_and_agent()
    curriculum_loop(env, agent)
    if USE_PYGAME:
        pygame.quit()


if __name__ == "__main__":
    main()
