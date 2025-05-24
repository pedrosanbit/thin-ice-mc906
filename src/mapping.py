from enum import Enum

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

color_map = [
    (154, 205, 254),
    (192, 223, 255),
    (218, 240, 255),
    (187, 228, 255),
    (249, 217, 5),
    (156, 205, 254),
    (92, 216, 126),
    (255, 206, 207),
    (0, 79, 191),
    (133, 17, 45)
]

def get_color(index):
    return color_map[index]