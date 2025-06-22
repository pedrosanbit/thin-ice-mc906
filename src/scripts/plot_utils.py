# src/scripts/plot_utils.py

import os
import csv
import matplotlib.pyplot as plt

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
