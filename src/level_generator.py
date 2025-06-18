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

    def __init__(self, mean_steps: int, std_steps: float = 0.2, thick_ice_prob: float = 0.15, teleport_prob: float = 0.24):
        """
        mean_steps: número médio de passos esperados
        std_ratio: desvio padrão em relação à média (ex: 0.2 => 20%)
        """
        self.mean_steps = mean_steps
        self.std_steps= std_steps
        self.thick_ice_prob = thick_ice_prob
        self.teleport_prob = teleport_prob

    def add_single_coin_bag(self, grid, start) -> List[Tuple[int, int]]:
        """Adiciona exatamente um saco de moedas em uma célula válida (não WALL, START ou FINISH)."""
        sx, sy = start
        candidates = []
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_LENGTH):
                if (x, y) == (sx, sy):
                    continue
                if grid[y][x] in (Map.THICK_ICE.value, Map.THIN_ICE.value):
                    candidates.append((x, y))
        return [random.choice(candidates)] if candidates else []

    def _random_walk(self, use_uniform=False) -> Tuple[List[List[int]], Tuple[int, int], int]:
        grid = [[Map.WALL.value for _ in range(self.GRID_LENGTH)]
                for _ in range(self.GRID_HEIGHT)]

        fy = random.randint(0, self.GRID_HEIGHT - 1)
        fx = random.randint(0, self.GRID_LENGTH - 1)
        grid[fy][fx] = Map.FINISH.value

        cy, cx = fy, fx
        steps = 0
        teleports = []  # lista de teletransportes

        if use_uniform:
            max_steps = random.randint(1, self.mean_steps)
        else:
            max_steps = int(np.clip(
                np.random.normal(self.mean_steps, self.std_steps),
                1, 300
            ))

        DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # R, D, L, U
        dir_idx = random.randint(0, 3)  # direção inicial aleatória

        path = [(cy, cx)]  # salva o caminho principal

        tiles_samples = [
            Map.THICK_ICE.value for _ in range (int(self.thick_ice_prob * max_steps))
        ] + [
            Map.THIN_ICE.value for _ in range(max_steps - int(self.thick_ice_prob * max_steps) + 1)
        ] # Se forem gerados muito gelos finos, a probabilidade de gerar um gelo grosso vai aumentando com teto máximo de thick_ice_prob
        while steps < max_steps:
            # (1) # Verifica se já não existe um teleporte na fase
            # (2) # Verifica se o teleporte está longe o suficiente do ponto final
            # (3) # Tenta a probabilidade de teleporte
            if not teleports \
                and steps > 3 and steps < max_steps - 3\
                and random.random() < (1 - (1 - self.teleport_prob) ** (1 / (max_steps-6))):
                teleport_positions = [
                    (y, x)
                    for y in range(1, self.GRID_HEIGHT - 1)
                    for x in range(1, self.GRID_LENGTH -1 )
                    if grid[y][x] == Map.WALL.value
                ]
                if teleport_positions:
                    ny, nx = random.choice(teleport_positions)
                    if grid[ny][nx] == Map.WALL.value:
                        grid[cy][cx] = Map.TELEPORT.value
                        teleports.append((cx, cy))
                        grid[ny][nx] = Map.TELEPORT.value
                        teleports.append((nx, ny))
                        cy, cx = ny, nx 
                        continue  # reinicia o loop após criar o teleporte

            probs = [0.0] * 4
            probs[dir_idx] = 0.4
            probs[(dir_idx + 1) % 4] = 0.25
            probs[(dir_idx - 1) % 4] = 0.25
            probs[(dir_idx + 2) % 4] = 0.1


            # Normaliza para evitar erros
            total = sum(probs)
            probs = [p / total for p in probs]

            # Testa opções viáveis com as chances acima
            options = []
            for i, (dy, dx) in enumerate(DIRECTIONS):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < self.GRID_HEIGHT and 0 <= nx < self.GRID_LENGTH:
                    tile = grid[ny][nx]
                    if tile not in (Map.FINISH.value, Map.THICK_ICE.value, Map.TELEPORT.value):
                        if tile == Map.THIN_ICE.value:
                            if random.choice(tiles_samples) != Map.THICK_ICE.value:
                                continue                      # (4) considera a probabilidade de gerar um gelo grosso
                        options.append((i, ny, nx))

            if not options:
                break

            # Escolhe a próxima direção com peso
            indices = [i for (i, _, _) in options]
            weights = [probs[i] for i in indices]
            chosen = random.choices(options, weights=weights, k=1)[0]
            dir_idx, cy, cx = chosen

            if grid[cy][cx] == Map.WALL.value:
                grid[cy][cx] = Map.THIN_ICE.value
                tiles_samples.pop(-1)  # remove um gelo fino do espaço amostral
            elif grid[cy][cx] == Map.THIN_ICE.value:
                grid[cy][cx] = Map.THICK_ICE.value
                tiles_samples.pop(0)  # remove um gelo grosso do espaço amostral

            path.append((cy, cx))
            steps += 1

        start = (cx, cy)
        return grid, start, [], [], [], teleports, steps


    def build_random_levels(self, total_levels: int, output_folder=None, extra_levels: int = 0) -> str:
        if output_folder is None:
            output_folder = f"procedural_generated/mean_{self.mean_steps:04}"


        total_to_generate = total_levels + extra_levels
        indices = list(range(total_to_generate))
        random.shuffle(indices)

        for idx_pos, idx in enumerate(indices):
            use_uniform = (idx_pos >= total_levels // 2)
            success, tries = False, 0

            while not success and tries < self.MAX_ATTEMPTS:
                tries += 1
                grid, start, coin_bags, keys, blocks, teleports, steps = self._random_walk(use_uniform=use_uniform)

                if steps < 1 or steps > 300:
                    continue

                sx, sy = start
                if grid[sy][sx] == Map.THICK_ICE.value:
                    continue

                # 🎯 50% de chance de adicionar um saco de moedas
                if random.random() < 0.5:
                    coin_bags = self.add_single_coin_bag(grid, start)

                encode_levels_to_txt(output_folder, idx, grid, start, coin_bags, keys, blocks, teleports, steps)
                success = True

        return output_folder