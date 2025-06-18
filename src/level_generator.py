import random
import numpy as np
from typing import List, Tuple

from src.mapping import Map
from src.levels import Level, encode_levels_to_txt


class LevelGenerator:
    """Gera fases procedurais para o Thin Ice com controle por média e desvio padrão."""

    GRID_HEIGHT = 15
    GRID_LENGTH = 19
    MAX_ATTEMPTS = 20

    def __init__(self, mean_steps: int, std_ratio: float = 0.2):
        """
        mean_steps: número médio de passos esperados
        std_ratio: desvio padrão em relação à média (ex: 0.2 => 20%)
        """
        self.mean_steps = mean_steps
        self.std_steps = max(1, int(std_ratio * mean_steps))  # evita std = 0

    def _random_walk(self, use_uniform=False) -> Tuple[List[List[int]], Tuple[int, int], int]:
        grid = [[Map.WALL.value for _ in range(self.GRID_LENGTH)]
                for _ in range(self.GRID_HEIGHT)]

        # coloca o ponto final
        fy = random.randint(0, self.GRID_HEIGHT - 1)
        fx = random.randint(0, self.GRID_LENGTH - 1)
        grid[fy][fx] = Map.FINISH.value

        cy, cx = fy, fx
        steps = 0

        if use_uniform:
            max_steps = random.randint(1, self.mean_steps)
        else:
            max_steps = int(np.clip(
                np.random.normal(self.mean_steps, self.std_steps),
                1, 300
            ))

        while steps <= max_steps:
            dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            options = []
            for dy, dx in dirs:
                ny, nx = cy + dy, cx + dx
                if not (0 <= ny < self.GRID_HEIGHT and 0 <= nx < self.GRID_LENGTH):
                    continue
                tile = grid[ny][nx]
                if tile in (Map.FINISH.value, Map.THICK_ICE.value):
                    continue
                options.append((ny, nx))

            if not options:
                break

            cy, cx = random.choice(options)
            if grid[cy][cx] == Map.WALL.value:
                grid[cy][cx] = Map.THIN_ICE.value
            elif grid[cy][cx] == Map.THIN_ICE.value:
                grid[cy][cx] = Map.THICK_ICE.value

            steps += 1

        start = (cx, cy)
        return grid, start, [], [], [], [], steps


    def build_random_levels(self, total_levels: int, output_folder=None) -> str:
        if output_folder is None:
            output_folder = f"mean_{self.mean_steps:04}"

        indices = list(range(total_levels))
        random.shuffle(indices)  # embaralha a ordem dos índices

        for idx_pos, idx in enumerate(indices):
            use_uniform = (idx_pos >= total_levels // 2)  # metade normal, metade uniforme
            success, tries = False, 0

            while not success and tries < self.MAX_ATTEMPTS:
                tries += 1
                grid, start, coin_bags, keys, blocks, teleports, steps = self._random_walk(use_uniform=use_uniform)

                if steps < 1 or steps > 300:
                    continue

                sx, sy = start
                if grid[sy][sx] == Map.THICK_ICE.value:
                    continue

                encode_levels_to_txt(output_folder, idx, grid, start, coin_bags, keys, blocks, teleports, steps)
                print(f"[INFO] Fase {idx:04} gerada com {steps} passos. {'(uniforme)' if use_uniform else '(normal)'}")
                success = True

            if not success:
                print(f"[ERRO] Nível {idx} falhou após {self.MAX_ATTEMPTS} tentativas.")

        return output_folder
