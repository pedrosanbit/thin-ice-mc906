# src/level_generator/teleport.py

import random

from src.mapping import Map
from src.mapping import GRID_HEIGHT, GRID_WIDTH, CELL_SIZE
from src.level_generator.validation import *

def add_teleport(self):
    if len(self.teleports) >= 2:
        print("[!] Apenas um par de teletransporte é permitido por fase.")
        return

    if self.teleport_stage == 0:
        if not is_valid_tile(self, exclude_start=True):
            print("[!] Tile inválido para entrada de teleporte.")
            return
        if is_tile_occupied(self, self.player_x, self.player_y):
            print("[!] Tile já contém item.")
            return
        if not _has_valid_teleport_exit(self):
            print("[!] Nenhuma saída possível para o teleporte.")
            return

        self.teleport_temp = (self.player_x, self.player_y)
        self.teleport_stage = 1
        print("[i] Entrada do teleporte colocada.")
        return

    elif self.teleport_stage == 1:
        valid_walls = _find_valid_teleport_exits(self)
        if not valid_walls:
            print("[!] Nenhuma parede válida para saída de teleporte.")
            self.teleport_temp = None
            self.teleport_stage = 0
            return

        exit_pos = random.choice(valid_walls)
        self.teleports.append(self.teleport_temp)
        self.teleports.append(exit_pos)

        tx1, ty1 = self.teleport_temp
        tx2, ty2 = exit_pos
        self.grid[ty1][tx1] = Map.TELEPORT.value
        self.grid[ty2][tx2] = Map.TELEPORT.value

        self.player_x, self.player_y = tx2, ty2
        self.teleport_temp = None
        self.teleport_stage = 0
        print("[✓] Teletransporte criado. Jogador movido para a saída.")

def _has_valid_teleport_exit(self):
    return bool(_find_valid_teleport_exits(self))

def _find_valid_teleport_exits(self):
        valid = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] != Map.WALL.value:
                    continue
                adjacents = [(x + dx, y + dy) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]]
                valid_adj = sum(1 for ax, ay in adjacents
                                if 0 <= ax < GRID_WIDTH and 0 <= ay < GRID_HEIGHT and is_valid_tile_at(self, ax, ay))
                invalid_adj = sum(1 for ax, ay in adjacents
                                  if 0 <= ax < GRID_WIDTH and 0 <= ay < GRID_HEIGHT and (ax, ay) in self.forbidden_area)
                if valid_adj >= 1 and invalid_adj == 0:
                    valid.append((x, y))
        return valid