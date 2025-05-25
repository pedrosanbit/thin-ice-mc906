from mapping import Map
import copy

class Level:
    def __init__(self, grid, start, coin_bags, keys, blocks, total_tiles):
        self.grid = grid
        self.start = start
        self.coin_bags = coin_bags
        self.keys = keys
        self.blocks = blocks
        self.total_tiles = total_tiles
    
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
    ], (14, 10), [], [], [], 12),
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
    ], (2, 10), [], [], [], 19),
    Level([
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.FINISH.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, 
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, 
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value, 
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19
    ], (14, 7), [], [], [], 25),
    Level([
        [Map.EMPTY.value] * 19,
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.WALL.value, Map.FINISH.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.EMPTY.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19
    ], (3, 7), [(7, 7)], [], [], 43),
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
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.FINISH.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.EMPTY.value
        ],
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19
    ], (14, 7), [(10, 10)], [], [], 41),
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
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [Map.EMPTY.value] * 19
    ], (2, 10), [(10, 11)], [], [], 41),
    Level([
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
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.FINISH.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THICK_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19
    ], (14, 7), [(10, 11)], [], [], 66),
    Level([
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [Map.EMPTY.value] * 19,
        [
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THICK_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THICK_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THICK_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.FINISH.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.EMPTY.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THICK_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THICK_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.WALL.value,
            Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.WALL.value, Map.WALL.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value, Map.THIN_ICE.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ],
        [
            Map.EMPTY.value, Map.EMPTY.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.WALL.value, Map.WALL.value, Map.WALL.value,
            Map.WALL.value, Map.EMPTY.value, Map.EMPTY.value
        ]
    ], (6, 5), [(2, 10)], [], [], 82)
]

def get_level(index):
    return copy.deepcopy(levels[index])