### src/level_generator/save.py
import os
from collections import deque
from src.levels import encode_levels_to_txt
from src.mapping import *

def _mark_forbidden_area(creator):
    visited = set()
    queue = deque([creator.original_start])
    forbidden = set()

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        forbidden.add((x, y))

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                tile = creator.grid[ny][nx]
                if tile in (creator.Map.THIN_ICE.value, creator.Map.THICK_ICE.value):
                    if (nx, ny) not in visited:
                        queue.append((nx, ny))
                elif tile == creator.Map.WALL.value:
                    forbidden.add((nx, ny))

    creator.forbidden_area = forbidden

def save_level(creator):
    from src.level_generator.validation import can_save_level
    if not can_save_level(creator):
        print("[!] Tile atual não é válido para salvar a fase.")
        return

    folder = creator.load_folder
    os.makedirs(os.path.join("data", "levels", folder), exist_ok=True)
    index = len(os.listdir(os.path.join("data", "levels", folder)))
    total_tiles = sum([row.count(creator.Map.THIN_ICE.value) for row in creator.grid])
    encode_levels_to_txt(folder, index, creator.grid, creator.start,
                         creator.coin_bags, creator.keys, [], creator.teleports, total_tiles)
    print(f"[✓] Fase salva como level_{index:04}.txt")
    import pygame
    pygame.quit()
