from mapping import Map, char_to_level_map, get_level_file_name
import copy
import os

# Inverso para salvar com caracteres simplificados
level_map_to_char = {v: k for k, v in char_to_level_map.items()}

class Level:
    def __init__(self, grid, start, coin_bags, keys, blocks, total_tiles):
        self.grid = grid
        self.start = start
        self.coin_bags = coin_bags
        self.keys = keys
        self.blocks = blocks
        self.total_tiles = total_tiles

def encode_txt_to_levels(txt_path, index):
    coin_bags = []
    keys = []
    blocks = []
    start = (0, 0)
    grid = []

    with open(txt_path, "r", encoding="utf-8") as f:
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
                map_enum = char_to_level_map.get(char, Map.EMPTY)
                row.append(map_enum.value)
            grid.append(row)

    total_tiles = sum(
        1 for row in grid for val in row
        if val not in (Map.EMPTY.value, Map.WALL.value)
    ) + sum(
        1 for row in grid for val in row if val == Map.THICK_ICE.value
    )

    return Level(grid, start, coin_bags, keys, blocks, total_tiles)


def encode_levels_to_txt(level, index):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(repo_root, "data", "levels")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{get_level_file_name(index)}.txt")

    os.makedirs(os.path.dirname(path), exist_ok=True)
        
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"START:{level.start[1]},{level.start[0]}\n")
            f.write(f"TOTAL_TILES:{level.total_tiles}\n")
            f.write(f"COIN_BAGS:{';'.join(f'{y},{x}' for x, y in level.coin_bags)}\n")
            f.write(f"KEYS:{';'.join(f'{y},{x}' for x, y in level.keys)}\n")
            f.write(f"BLOCKS:{';'.join(f'{y},{x}' for x, y in level.blocks)}\n")

            for i, row in enumerate(level.grid):
                line = ""
                for j, val in enumerate(row):
                    coord = (i, j)
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

def get_level(index):
    path = os.path.join("data", "levels", f"{get_level_file_name(index)}.txt")
    with open(path, "r", encoding="utf-8") as f:
        start = (0, 0)
        total_tiles = 0
        coin_bags, keys, blocks = [], [], []

        while True:
            line = f.readline()
            if not line or not line.strip():
                break
            if line.startswith("START:"):
                x, y = map(int, line.strip().split(":")[1].split(","))
                start = (x, y)
            elif line.startswith("TOTAL_TILES:"):
                total_tiles = int(line.strip().split(":")[1])
            elif line.startswith("COIN_BAGS:"):
                items = line.strip().split(":")[1]
                coin_bags = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
            elif line.startswith("KEYS:"):
                items = line.strip().split(":")[1]
                keys = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
            elif line.startswith("BLOCKS:"):
                items = line.strip().split(":")[1]
                blocks = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
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

        return Level(grid, start, coin_bags, keys, blocks, total_tiles)