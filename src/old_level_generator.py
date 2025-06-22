import random
import numpy as np
from typing import List, Tuple

from src.mapping import Map
from src.levels import Level, encode_levels_to_txt


class LevelGenerator:
    GRID_HEIGHT = 15
    GRID_LENGTH = 19
    MAX_ATTEMPTS = 20

    def __init__(self, mean_steps: int, std_steps: float = 0.2, teleport_prob: float = 0.0):
        self.mean_steps = mean_steps
        self.std_steps = max(1, int(std_steps * mean_steps))
        self.teleport_prob = teleport_prob

    def maybe_create_teleport(self, grid, cy, cx, steps, max_steps, teleports) -> Tuple[bool, int, int]:
        if not teleports or steps <= 3 or steps >= max_steps - 3:
            return False, cy, cx

        prob = 1 - (1 - self.teleport_prob) ** (1 / (max_steps - 6))
        if random.random() > prob:
            return False, cy, cx

        candidates = [(y, x) for y in range(1, self.GRID_HEIGHT - 1)
                             for x in range(1, self.GRID_LENGTH - 1)
                             if grid[y][x] == Map.WALL.value]

        if not candidates:
            return False, cy, cx

        ny, nx = random.choice(candidates)
        grid[cy][cx] = Map.TELEPORT.value
        teleports.append((cx, cy))
        grid[ny][nx] = Map.TELEPORT.value
        teleports.append((nx, ny))
        return True, ny, nx

    def add_coin_bags(self, grid, start) -> List[Tuple[int, int]]:
        # Adiciona um saco de moedas fora do ponto inicial ou final
        sx, sy = start
        valid_cells = [
            (x, y) for y in range(self.GRID_HEIGHT)
                   for x in range(self.GRID_LENGTH)
                   if grid[y][x] in (Map.THIN_ICE.value, Map.THICK_ICE.value)
                   and (x, y) != (sx, sy)
        ]
        return [random.choice(valid_cells)] if valid_cells else []

    def _random_walk(self, use_uniform=False) -> Tuple[List[List[int]], Tuple[int, int], int]:
        grid = [[Map.WALL.value for _ in range(self.GRID_LENGTH)] for _ in range(self.GRID_HEIGHT)]
        fy, fx = random.randint(0, self.GRID_HEIGHT - 1), random.randint(0, self.GRID_LENGTH - 1)
        grid[fy][fx] = Map.FINISH.value

        cy, cx = fy, fx
        steps = 0
        teleports = []

        max_steps = random.randint(1, self.mean_steps) if use_uniform else int(np.clip(
            np.random.normal(self.mean_steps, self.std_steps), 1, 300))

        while steps < max_steps:
            created, cy, cx = self.maybe_create_teleport(grid, cy, cx, steps, max_steps, teleports)
            if created:
                continue

            dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            options = []
            for dy, dx in dirs:
                ny, nx = cy + dy, cx + dx
                if not (0 <= ny < self.GRID_HEIGHT and 0 <= nx < self.GRID_LENGTH):
                    continue
                tile = grid[ny][nx]

                if tile in (Map.FINISH.value, Map.THICK_ICE.value, Map.TELEPORT.value):
                    continue

                if tile == Map.WALL.value:
                    options.append((ny, nx, 'thin'))
                elif tile == Map.THIN_ICE.value and random.random():
                    options.append((ny, nx, 'thick'))

            if not options:
                break

            ny, nx, action = random.choice(options)
            if action == 'thin':
                grid[ny][nx] = Map.THIN_ICE.value
            elif action == 'thick':
                grid[ny][nx] = Map.THICK_ICE.value

            cy, cx = ny, nx
            steps += 1

        start = (cx, cy)
        return grid, start, self.add_coin_bags(grid, start), [], [], teleports, steps

    def generate_valid_level(self, idx: int, use_uniform: bool, output_folder: str) -> bool:
        """
        Tenta gerar um nível válido e salvá-lo. Retorna True se teve sucesso.
        """
        for _ in range(self.MAX_ATTEMPTS):
            grid, start, coin_bags, keys, blocks, teleports, steps = self._random_walk(use_uniform)

            # Restrições de validade:
            if not (1 <= steps <= 300):
                continue
            sx, sy = start
            if grid[sy][sx] == Map.THICK_ICE.value:
                continue

            # Nível considerado válido → salva
            encode_levels_to_txt(
                output_folder,
                idx,
                grid,
                start,
                coin_bags,
                keys,
                blocks,
                teleports,
                steps
            )
            return True  # sucesso
        return False  # falhou após MAX_ATTEMPTS


    def build_random_levels(self, total_levels: int, output_folder=None) -> str:
        output_folder = output_folder or f"mean_{self.mean_steps:04}"
        indices = list(range(total_levels))
        random.shuffle(indices)

        for idx_pos, idx in enumerate(indices):
            use_uniform = (idx_pos >= total_levels // 2)
            success = self.generate_valid_level(idx, use_uniform, output_folder)
            
            #if not success:
            #    print(f"[⚠️] Falha ao gerar o nível {idx:04} após {self.MAX_ATTEMPTS} tentativas.")
            #else:
            #    print(f"[✓] Nível {idx:04} gerado com sucesso. {'(uniforme)' if use_uniform else '(normal)'}")

        return output_folder


