# src/scripts/train.py
 
import os
import numpy as np
from src.env.solver_env import SolverEnv
from old_level_generator import LevelGenerator
from src.utils import draw_game_screen
from plot_utils import plot_batch_summary, save_round_summary_csv


from src.scripts.trainer_utils import setup_directories, initialize_environment_and_agent, validate_on_original_game
import pygame

# ------------------ Configurações Gerais ------------------

# Episódios e passos por rodada
EPISODES_PER_ROUND = 400       # Número de episódios por rodada de treinamento
STEPS_PER_EP = 400             # Número máximo de passos por episódio

# Ambiente
USE_PYGAME = False             # Ativa ou não a visualização com Pygame
ALLOW_FAILURE_PROGRESSION = False  # Permite seguir para próxima fase mesmo após falha

# Curriculum Learning
INITIAL_MEAN = 6               # Média inicial de passos usada para gerar fases
STD_RATIO = 0.5                # Desvio padrão relativo na geração de fases
MAX_MEAN = 160                 # Limite superior da média de passos
GROWTH = 1.25                  # Fator de crescimento da dificuldade
SUCCESS_THRESHOLD = 0.85       # Taxa mínima de sucesso para aumentar a dificuldade
WINDOW_SIZE = 300             # Janela para média móvel de taxa de sucesso

# Agente DQN
BUFFER_SIZE = 50_000           # Capacidade do replay buffer
UPDATE_FREQ = 4                # Frequência de atualizações da rede
MIN_BUFFER_SIZE = 1000         # Tamanho mínimo do buffer antes de treinar
USE_ACTION_MASK = True  # Altere para False para treinar sem máscara


# Validação
USE_VALIDATION = False         # Ativa ou não validação periódica nas fases reais


def run_episode(env, agent):
    s, info = env.reset()
    total_reward, solved = 0, False
    for t in range(STEPS_PER_EP):
        a = agent.act(s, info["action_mask"] if USE_ACTION_MASK else None)
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

def curriculum_loop(env, agent):
    mean_steps = INITIAL_MEAN
    success_history = []
    tile_ratio_history = []
    for round_id in range(200_000):
        lg = LevelGenerator(mean_steps=int(mean_steps), std_steps=STD_RATIO)
        level_dir = lg.build_random_levels(EPISODES_PER_ROUND, extra_levels=100)
        env.change_level_folder(level_dir, 0)

        batch_results = []
        for ep in range(EPISODES_PER_ROUND):
            info, solved = run_episode(env, agent)
            batch_results.append(info["result"])
            success_history.append(int(solved))
            tile_ratio_history.append(env.game.current_tiles / env.game.level.total_tiles if solved else 0.0)

        val_ratio = validate_on_original_game(agent, USE_ACTION_MASK) if USE_VALIDATION else 0.0

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
        from src.utils import init_screen
        screen, font = init_screen()
    env, agent = initialize_environment_and_agent(
        steps_per_episode=STEPS_PER_EP,
        buffer_size=BUFFER_SIZE,
        allow_failure_progression=ALLOW_FAILURE_PROGRESSION,
        use_action_mask=USE_ACTION_MASK
    )
    curriculum_loop(env, agent)
    if USE_PYGAME:
        pygame.quit()

if __name__ == "__main__":
    main()
