from mapping import Map, char_to_map, map_to_char
import copy
import os
class Level:
    def __init__(self, grid, start, coin_bags, keys, blocks, total_tiles):
        self.grid = grid
        self.start = start
        self.coin_bags = coin_bags
        self.keys = keys
        self.blocks = blocks
        self.total_tiles = total_tiles
    
def get_level_file_name(index):
    if index < 10:
        return f"level_00{index}.txt"
    elif index < 100:
        return f"level_0{index}.txt"
    return f"level_{index}.txt"

def encode_levels_to_txt(level, idx):
    try:
        from levels import Map
    except ImportError:
        print("[ERRO] Enum Map não encontrado.")
        return

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(repo_root, "data", "levels")
    os.makedirs(output_dir, exist_ok=True)

    path = os.path.join(output_dir, get_level_file_name(idx))

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"START:{level.start[0]},{level.start[1]}\n")
            f.write(f"TOTAL_TILES:{level.total_tiles}\n")
            f.write(f"COIN_BAGS:{';'.join(f'{x},{y}' for x, y in level.coin_bags)}\n")
            f.write(f"KEYS:{';'.join(f'{x},{y}' for x, y in level.keys)}\n")
            f.write(f"BLOCKS:{';'.join(f'{x},{y}' for x, y in level.blocks)}\n")

            # Escreve a grade
            for row in level.grid:
                line = ''.join(map_to_char[Map(cell) if isinstance(cell, int) else cell] for cell in row)
                f.write(line + "\n")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar nível {idx}: {e}")

def get_level(index):
    path = f"data/levels/{get_level_file_name(index)}"
    with open(path, "r", encoding="utf-8") as f:
        start = (0, 0)
        total_tiles = 0
        coin_bags, keys, blocks = [], [], []

        # Lê cabeçalhos
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
                break  # chegou na grade

        # Lê a grade
        grid = [list(line.strip()) for line in [line] + f.readlines()]
        grid = [[char_to_map.get(c, Map.EMPTY).value for c in row] for row in grid]

        return Level(grid, start, coin_bags, keys, blocks, total_tiles)



