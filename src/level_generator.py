# src/level_generator.py
import random
from typing import List, Tuple

from src.mapping import Map
from src.levels import Level
from src.level_set import LevelSet, Progression   # ⬅️ NOVO

class LevelGenerator:
    """Gera fases procedurais para o Thin Ice e grava via LevelSet."""

    GRID_HEIGHT = 15
    GRID_LENGTH = 19
    MAX_ATTEMPTS = 20

    def __init__(self, min_size: int, max_size: int):
        self.min_size = min_size
        self.max_size = max_size

    def _random_walk(self) -> Tuple[List[List[int]], Tuple[int, int], int]:
        grid = [[Map.WALL.value for _ in range(self.GRID_LENGTH)]
                for _ in range(self.GRID_HEIGHT)]

        fy, fx = random.randrange(self.GRID_HEIGHT), random.randrange(self.GRID_LENGTH)
        grid[fy][fx] = Map.FINISH.value

        cy, cx = fy, fx
        steps = 0

        while steps < self.max_size:
            dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            opts = []
            for dy, dx in dirs:
                ny, nx = cy + dy, cx + dx
                if not (0 <= ny < self.GRID_HEIGHT and 0 <= nx < self.GRID_LENGTH):
                    continue
                tile = grid[ny][nx]
                if tile in (Map.FINISH.value, Map.THICK_ICE.value):
                    continue
                opts.append((ny, nx))

            if not opts:
                break

            cy, cx = random.choice(opts)
            if grid[cy][cx] == Map.WALL.value:
                grid[cy][cx] = Map.THIN_ICE.value
            elif grid[cy][cx] == Map.THIN_ICE.value:
                grid[cy][cx] = Map.THICK_ICE.value
            steps += 1

        start = (cx, cy)
        return grid, start, steps

    def build_random_levels(self, total_levels: int, output_folder: str | None = None
                            ) -> LevelSet:
        """
        Gera *total_levels* fases entre `min_size` e `max_size` passos e
        devolve um objeto LevelSet pronto para uso.
        """
        if output_folder is None:
            output_folder = f"type_{self.min_size:04}_{self.max_size:04}"

        level_set = LevelSet(
            folder=output_folder,
            max_index=total_levels - 1,
            progression=Progression.RANDOM,
        )

        idx = 0
        while idx < total_levels:
            success = False
            for _try in range(self.MAX_ATTEMPTS):
                grid, start, steps = self._random_walk()
                if steps < self.min_size:
                    continue
                sx, sy = start
                if grid[sy][sx] == Map.THICK_ICE.value:
                    continue     

                level = Level(grid, start, [], [], [], [])
                level_set.save_level(level, idx)
                print(f"[INFO] Fase {idx:04} gerada com {steps} passos.")
                success = True
                idx += 1
                break

            if not success:
                print(f"[ERRO] Falha ao gerar nível {idx} após {self.MAX_ATTEMPTS} tentativas.")

        return level_set
