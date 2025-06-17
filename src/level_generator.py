# src/level_generator.py
import random
from typing import List, Tuple

from src.mapping import Map
from src.levels import Level, encode_levels_to_txt


class LevelGenerator:
    """Gera fases procedurais para o Thin Ice."""

    GRID_HEIGHT = 15
    GRID_LENGTH = 19
    MAX_ATTEMPTS = 20

    def __init__(self, min_size: int, max_size: int):
        self.min_size = min_size
        self.max_size = max_size

    def _random_walk(self) -> Tuple[List[List[int]], Tuple[int, int], int]:
        """
        Constrói uma grade e devolve (grid, coord_start, passos).

        – Não mantém 'visited': o caminho pode revisitar gelo fino
          (convertendo-o em gelo grosso).  
        – Nunca permite voltar ao FINISH.  
        – Nunca pisa num vizinho que já seja THICK_ICE.
        """
        grid = [[Map.WALL.value for _ in range(self.GRID_LENGTH)]
                for _ in range(self.GRID_HEIGHT)]

        # coloca o ponto final
        fy = random.randint(0, self.GRID_HEIGHT - 1)
        fx = random.randint(0, self.GRID_LENGTH - 1)
        grid[fy][fx] = Map.FINISH.value

        cy, cx = fy, fx            # posição corrente
        steps = 0

        max_steps = random.randint(self.min_size, self.max_size)
        while steps <= max_steps:
            dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            options = []
            for dy, dx in dirs:
                ny, nx = cy + dy, cx + dx
                if not (0 <= ny < self.GRID_HEIGHT and 0 <= nx < self.GRID_LENGTH):
                    continue                         # fora da grade
                tile = grid[ny][nx]
                if tile == Map.FINISH.value:         # (2) não volta ao FINISH
                    continue
                if tile == Map.THICK_ICE.value:      # (3) evita gelo grosso
                    continue
                options.append((ny, nx))

            if not options:
                break                                # sem movimento possível

            cy, cx = random.choice(options)
            if grid[cy][cx] == Map.WALL.value:
                grid[cy][cx] = Map.THIN_ICE.value
            elif grid[cy][cx] == Map.THIN_ICE.value:
                grid[cy][cx] = Map.THICK_ICE.value

            steps += 1

        start = (cx, cy)  # (x, y) — nota: encode_levels_to_txt assume (x,y)
        coin_bags = []
        keys = []
        blocks = []
        teleports = []
        return grid, start, coin_bags, keys, blocks, teleports, steps

    def build_random_levels(self, total_levels: int, output_folder = None) -> str:
        if output_folder == None:
            output_folder = f"type_{self.min_size:04}_{self.max_size:04}"

        idx = 0
        while idx < total_levels:
            success, tries = False, 0
            while not success and tries < self.MAX_ATTEMPTS:
                tries += 1
                grid, start, coin_bags, keys, blocks, teleports, steps = self._random_walk()
                if steps < self.min_size:
                    continue         

                # início não pode ser THICK_ICE
                sx, sy = start
                if grid[sy][sx] == Map.THICK_ICE.value:
                    continue

                encode_levels_to_txt(output_folder, idx, grid, start, coin_bags, keys, blocks, teleports, steps)
                print(f"[INFO] Fase {idx:04} gerada com {steps} passos.")
                idx += 1
                success = True

            if not success:
                print(f"[ERRO] Nível {idx} falhou após {self.MAX_ATTEMPTS} tentativas.")

        return output_folder
