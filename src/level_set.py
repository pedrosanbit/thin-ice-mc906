# src/level_set.py
"""Wrapper para conjuntos de fases do Thin Ice.

Inclui a lógica de serialização (\*.txt → Level e vice‑versa)."""

from __future__ import annotations

import os
import random
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

from src.levels import Level  # usa a classe‑modelo já existente
from src.mapping import Map, char_to_level_map

# Mapeamento inverso para escrita de arquivo
level_map_to_char = {v: k for k, v in char_to_level_map.items()}


# --------------------------------------------------
# Estratégias de progressão
# --------------------------------------------------
class Progression(Enum):
    SEQUENTIAL = "sequential"   # 0,1,2,…,max_index; termina no último
    RANDOM = "random"           # sorteia um índice a cada fase (loop infinito)


# --------------------------------------------------
# LevelSet
# --------------------------------------------------
class LevelSet:
    """Representa um diretório com níveis em texto.

    Fornece utilitários para carregar (=decodificar) e salvar (=codificar) objetos
    :class:`Level`.
    """

    def __init__(
        self,
        folder: str,
        max_index: int,
        *,
        progression: Progression = Progression.SEQUENTIAL,
        seed: int = 42,
    ) -> None:
        self.folder = folder
        self.max_index = max_index
        self.progression = progression
        self._rng = random.Random(seed)

        # Diretório base data/levels/<folder>
        repo_root = Path(__file__).resolve().parent.parent  # …/src → repo root
        self.base_dir: Path = repo_root / "data" / "levels" / folder
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Caminho de arquivo
    # --------------------------------------------------
    def _path(self, index: int) -> Path:
        return self.base_dir / f"level_{index:04}.txt"

    # --------------------------------------------------
    # Serialização → txt
    # --------------------------------------------------
    def save_level(self, level: Level, index: int) -> None:
        """Salva *level* no índice dado usando o formato texto."""
        path = self._path(index)

        try:
            with path.open("w", encoding="utf-8") as f:
                # Cabeçalho
                f.write(f"START:{level.start[0]},{level.start[1]}\n")
                f.write(f"TOTAL_TILES:{level.total_tiles}\n")
                f.write(f"COIN_BAGS:{';'.join(f'{x},{y}' for x, y in level.coin_bags)}\n")
                f.write(f"KEYS:{';'.join(f'{x},{y}' for x, y in level.keys)}\n")
                f.write(f"BLOCKS:{';'.join(f'{x},{y}' for x, y in level.blocks)}\n")
                f.write(f"TELEPORTS:{';'.join(f'{x},{y}' for x, y in level.teleports)}\n")

                # Grid — percorre (x,y) usando o wrapper Grid
                for y in range(level.grid.height):
                    line = ""
                    for x in range(level.grid.width):
                        coord = (x, y)
                        val   = level.grid.tile(x, y).value

                        if coord == level.start:
                            line += "A"
                        elif coord in level.coin_bags:
                            line += "8"
                        elif coord in level.keys:
                            if val == Map.THIN_ICE.value:
                                line += "B"
                            elif val == Map.THICK_ICE.value:
                                line += "C"
                            elif val == Map.TILE.value:
                                line += "D"
                            else:
                                line += level_map_to_char.get(Map(val), "0")
                        elif coord in level.blocks:
                            line += "6"
                        else:
                            line += level_map_to_char.get(Map(val), "0")
                    f.write(line + "\n")
        except Exception as e:
            print(f"[ERRO] Falha ao salvar nível {index}: {e}")

    # --------------------------------------------------
    # Desserialização ← txt
    # --------------------------------------------------
    def get_level(self, index: int) -> Level:
        """Carrega e retorna um :class:`Level`."""
        path = self._path(index)
        if not path.exists():
            raise FileNotFoundError(path)

        with path.open("r", encoding="utf-8") as f:
            start: Tuple[int, int] = (0, 0)
            total_tiles = 0
            coin_bags: List[Tuple[int, int]] = []
            keys: List[Tuple[int, int]] = []
            blocks: List[Tuple[int, int]] = []
            teleports: List[Tuple[int, int]] = []

            # Cabeçalho
            while True:
                line = f.readline()
                if not line or not line.strip():
                    break
                if line.startswith("START:"):
                    x, y = map(int, line.strip().split(":")[1].split(","))
                    start = (x, y)
                elif line.startswith("TOTAL_TILES:"):
                    total_tiles = int(line.strip().split(":")[1]) - 1
                elif line.startswith("COIN_BAGS:"):
                    items = line.strip().split(":")[1]
                    coin_bags = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
                elif line.startswith("KEYS:"):
                    items = line.strip().split(":")[1]
                    keys = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
                elif line.startswith("BLOCKS:"):
                    items = line.strip().split(":")[1]
                    blocks = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
                elif line.startswith("TELEPORTS:"):
                    items = line.strip().split(":")[1]
                    teleports = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
                else:
                    break

            # Grid
            grid_lines = [line.strip() for line in [line] + f.readlines()]
            grid: List[List[int]] = []
            for i, line in enumerate(grid_lines):
                row: List[int] = []
                for j, char in enumerate(line):
                    row.append(char_to_level_map.get(char, Map.EMPTY).value)
                grid.append(row)

            return Level(grid, start, coin_bags, keys, blocks, teleports)

    # --------------------------------------------------
    # Progressão
    # --------------------------------------------------
    def next_index(self, current_index: int) -> Optional[int]:
        if self.progression is Progression.SEQUENTIAL:
            return None if current_index >= self.max_index else current_index + 1
        return self._rng.randint(0, self.max_index)

    # conveniência
    def __len__(self) -> int:
        return self.max_index + 1
