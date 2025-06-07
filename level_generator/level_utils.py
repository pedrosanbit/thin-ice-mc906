from level_generator.level_utils import evaluate_level

import os
from PIL import Image
import numpy as np
from mapping import Map, char_to_level_map
from levels import Level


def count_ice_tiles(grid):
    thin = np.sum(grid == Map.THIN_ICE.value)
    thick = np.sum(grid == Map.THICK_ICE.value)
    return thin, thick, thin + 2 * thick


def compute_coverage(grid, start_pos):
    from collections import deque
    visited = set()
    queue = deque([start_pos])
    covered_weight = 0

    while queue:
        r, c = queue.popleft()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        val = grid[r, c]
        if val == Map.THIN_ICE.value:
            covered_weight += 1
        elif val == Map.THICK_ICE.value:
            covered_weight += 2
        else:
            continue
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]:
                if grid[nr, nc] in [Map.THIN_ICE.value, Map.THICK_ICE.value] and (nr, nc) not in visited:
                    queue.append((nr, nc))

    return covered_weight


def evaluate_level(level: Level):
    grid = np.array(level.grid)
    thin, thick, total_weighted = count_ice_tiles(grid)
    if total_weighted == 0:
        return 0.0
    coverage = compute_coverage(grid, (level.start[0], level.start[1]))
    ratio = coverage / total_weighted
    return ratio

# Parâmetros fixos
tile_size = 20
cols, rows = 19, 15

# Caminho das imagens dos blocos
REF_TILE_PATH = os.path.join("data", "pictures", "tiles", "labels")

def carregar_tiles_de_referencia(ref_dir=REF_TILE_PATH):
    tile_examples = {}
    for label in os.listdir(ref_dir):
        label_dir = os.path.join(ref_dir, label)
        if os.path.isdir(label_dir):
            imgs = [f for f in os.listdir(label_dir) if f.endswith(".png")]
            if imgs:
                tile_path = os.path.join(label_dir, imgs[0])
                tile_img = Image.open(tile_path).resize((tile_size, tile_size), Image.NEAREST)
                tile_examples[label] = tile_img
    return tile_examples

# Reverso do char_to_level_map
level_to_char_map = {v: k for k, v in char_to_level_map.items()}

def reconstruir_imagem(grid, output_path):
    tile_examples = carregar_tiles_de_referencia()
    reconstructed = Image.new("RGB", (cols * tile_size, rows * tile_size))
    
    for i, row in enumerate(grid):
        for j, tile in enumerate(row):
            char = level_to_char_map.get(tile, None)
            if char is None:
                continue
            tile_img = tile_examples.get(char)
            if tile_img:
                reconstructed.paste(tile_img, (j * tile_size, i * tile_size))
    
    reconstructed.save(output_path)
