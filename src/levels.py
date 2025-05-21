from mapping import Map
import copy

class Level:
    def __init__(self, grid, start, coin_bags, keys, blocks):
        self.grid = grid
        self.start = start
        self.coin_bags = coin_bags
        self.keys = keys
        self.blocks = blocks
    
levels = [
    Level([
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.FINISH.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19
    ], (14, 10), [], [], []),
    Level([
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.WALL.value, Map.FINISH.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.EMPTY.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [Map.EMPTY.value] * 19
    ], (2, 10), [], [], [])
]

def get_level(index):
    return copy.deepcopy(levels[index])