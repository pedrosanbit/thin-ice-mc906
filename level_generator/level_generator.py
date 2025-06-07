import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from levels import Level
from mapping import Map

def gerar_level():
    coin_bags = []
    keys = []
    blocks = []
    teleports = [] 
    grid = []
    
    grid = [[Map.EMPTY for u in range(19)] for v in range(15)] 
    
    start = (0, 0)

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
                if char == '7':
                    teleports.append((i, j))  # NOVO
                map_enum = char_to_level_map.get(char, Map.EMPTY)
                row.append(map_enum.value)
            grid.append(row)

    total_tiles = sum(
        1 for row in grid for val in row
        if val not in (Map.EMPTY.value, Map.WALL.value)
    ) + sum(
        1 for row in grid for val in row if val == Map.THICK_ICE.value
    )

    return Level(grid, start, coin_bags, keys, blocks, total_tiles, teleports)