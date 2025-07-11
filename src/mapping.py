from enum import Enum


GRID_HEIGHT = 15
GRID_WIDTH = 19
CELL_SIZE = 32

class Map(Enum):
    EMPTY = 0
    WALL = 1
    THIN_ICE = 2
    THICK_ICE = 3
    LOCK = 4
    TILE = 5
    TELEPORT = 6
    FINISH = 7
    WATER = 8
    COIN_BAG = 9
    BLOCK = 10

char_to_level_map = {
    '0': Map.EMPTY,
    '1': Map.WALL,
    '2': Map.THIN_ICE,
    '3': Map.THICK_ICE,
    '4': Map.LOCK,
    '5': Map.TILE,
    '6': Map.THIN_ICE,  # THIN_ICE COM BLOCO
    '7': Map.TELEPORT,
    '8': Map.THIN_ICE,  # THIN ICE COM COIN_BAG
    '9': Map.FINISH,
    'A': Map.THIN_ICE,  # START
    'B': Map.THIN_ICE,  # THIN ICE COM KEY
    'C': Map.THICK_ICE, # THICK ICE COM KEY
    'D': Map.TILE,       # TILE COM KEY
    'E': Map.THICK_ICE  # THICK ICE COM BLOCO
}

level_map_to_char = {
    Map.WALL: '0',
    Map.WALL: '1',
    Map.THIN_ICE: '2',
    Map.THICK_ICE: '3',
    Map.LOCK: '4',
    Map.TILE: '5',
    Map.TELEPORT: '7',
    Map.FINISH: '9',
}

color_map = [
    (154, 205, 254),
    (70, 164, 255),
    (218, 240, 255),
    (255, 253, 252),
    (249, 217, 5),
    (156, 205, 254),
    (92, 216, 126),
    (255, 206, 207),
    (0, 79, 191),
    (133, 17, 45),
    (135, 209, 255)
]

def get_color(index):
    return color_map[index]

def get_level_file_name(index):
    if index < 10:
        return f"level_00{index}"
    elif index < 100:
        return f"level_0{index}"
    return f"level_{index}"