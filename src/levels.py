# /src/levels.py

from src.mapping import Map, char_to_level_map
import random
import copy
import os

level_map_to_char = {v: k for k, v in char_to_level_map.items()}

class Level:
    def __init__(
        self,
        grid,
        start,
        coin_bags,
        keys,
        blocks,
        teleports,
        total_tiles=None, 
        total_points=None
    ):
        self.grid       = grid
        self.start      = start
        self.coin_bags  = coin_bags
        self.keys       = keys
        self.blocks     = blocks
        self.teleports  = teleports

        # usa o valor passado se existir; caso contrário calcula
        self.total_tiles =  self.compute_total_tiles()
        
        self.total_points = self.compute_total_points()
        
    def compute_total_tiles(self):
        return sum(
            1 for row in self.grid for val in row if val == Map.THIN_ICE.value
        ) + sum(
            1 for row in self.grid for val in row if val == Map.THICK_ICE.value
        )
        
    def compute_total_points(self):
        return sum(
            1 for row in self.grid for val in row if val == Map.THIN_ICE.value
        ) + sum(
            2 for row in self.grid for val in row if val == Map.THICK_ICE.value
        ) + 100*len(self.coin_bags)
        
def get_level_path(folder, index):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(repo_root, "data", "levels")
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    path = os.path.join(output_dir, folder, f"level_{index:04}.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    return path
        
def encode_txt_to_levels(folder, index):
    coin_bags = []
    keys = []
    blocks = []
    teleports = [] 
    start = (0, 0)
    grid = []
    
    input_path = get_level_path(folder, index)

    with open(input_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        for i, line in enumerate(lines):
            row = []
            for j, char in enumerate(line):
                if char == 'A':
                    start = (i, j)
                if char == '8':
                    coin_bags.append((i, j))
                if char in ('B', 'C', 'D'):
                    keys.append((i, j))
                if char == '6':
                    blocks.append((i, j))
                if char == '7':
                    teleports.append((i, j))  # NOVO
                map_enum = char_to_level_map.get(char, Map.EMPTY)
                row.append(map_enum.value)
            grid.append(row)

    return Level(grid, start, coin_bags, keys, blocks, teleports)

def encode_levels_to_txt(level, folder, index):
    output_path = get_level_path(folder, index)
        
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"START:{level.start[0]},{level.start[1]}\n")
            f.write(f"TOTAL_TILES:{level.total_tiles}\n")
            f.write(f"COIN_BAGS:{';'.join(f'{x},{y}' for x, y in level.coin_bags)}\n")
            f.write(f"KEYS:{';'.join(f'{x},{y}' for x, y in level.keys)}\n")
            f.write(f"BLOCKS:{';'.join(f'{x},{y}' for x, y in level.blocks)}\n")
            f.write(f"TELEPORTS:{';'.join(f'{x},{y}' for x, y in level.teleports)}\n") 

            for i, row in enumerate(level.grid):
                line = ""
                for j, val in enumerate(row):
                    coord = (j, i)
                    if coord == level.start:
                        line += 'A'
                    elif coord in level.coin_bags:
                        line += '8'
                    elif coord in level.keys:
                        # Inferir tipo original se quiser, ou usar 'B' genérico
                        if val == Map.THIN_ICE.value:
                            line += 'B'
                        elif val == Map.THICK_ICE.value:
                            line += 'C'
                        elif val == Map.TILE.value:
                            line += 'D'
                        else:
                            line += level_map_to_char.get(Map(val), '0')
                    elif coord in level.blocks:
                        line += '6'
                    else:
                        line += level_map_to_char.get(Map(val), '0')
                f.write(line + "\n")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar nível {index}: {e}")

def get_level(folder, index):
    input_path = get_level_path(folder, index)
    
    with open(input_path, "r", encoding="utf-8") as f:
        start = (0, 0)
        total_tiles = 0
        coin_bags, keys, blocks, teleports = [], [], [], []

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

        grid_lines = [line.strip() for line in [line] + f.readlines()]
        grid = []
        for i, line in enumerate(grid_lines):
            row = []
            for j, char in enumerate(line):
                map_enum = char_to_level_map.get(char, Map.EMPTY)
                row.append(map_enum.value)
            grid.append(row)

        return Level(grid, start, coin_bags, keys, blocks, total_tiles, teleports)