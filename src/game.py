from levels import get_level
from mapping import Map

class Game:
    def __init__(self, num_level, level, player_x, player_y, points, current_points, keys_obtained, current_tiles, solved):
        self.num_level = num_level
        self.level = level
        self.player_x = player_x
        self.player_y = player_y
        self.points = points
        self.current_points = current_points
        self.keys_obtained = keys_obtained
        self.current_tiles = current_tiles
        self.solved = solved

    def load_level(self, num_level):
        self.level = get_level(num_level)
        self.current_tiles = 0
        self.player_x = self.level.start[0]
        self.player_y = self.level.start[1]

    def check_next_level(self):
        if self.level.grid[self.player_y][self.player_x] == Map.FINISH.value:
            self.num_level += 1
            self.current_points += self.current_tiles * 2
            self.points = self.current_points
            if self.current_tiles == self.level.total_tiles:
                self.solved += 1
            self.load_level(self.num_level)
            return True
        return False
    
    def check_game_over(self):
        rows = len(self.level.grid)
        cols = len(self.level.grid[0])
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]
        for dr, dc in directions:
            nr, nc = self.player_y + dr, self.player_x + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if self.level.grid[nr][nc] not in (Map.WALL.value, Map.WATER.value):
                    return
        self.current_points = self.points
        self.load_level(self.num_level)

    def check_coin_bag(self):
        for coin_bag in self.level.coin_bags:
            if self.player_x == coin_bag[0] and self.player_y == coin_bag[1]:
                self.current_points += 100
                self.level.coin_bags.remove(coin_bag)
                return

    def move_player(self, direction):
        new_x = self.player_x + direction[0]
        new_y = self.player_y + direction[1]

        if self.level.grid[new_y][new_x] in (Map.WALL.value, Map.WATER.value):
            return

        current_tile = self.level.grid[self.player_y][self.player_x]
        if current_tile == Map.THIN_ICE.value:
            self.level.grid[self.player_y][self.player_x] = Map.WATER.value
            self.current_tiles += 1
        elif current_tile == Map.THICK_ICE.value:
            self.level.grid[self.player_y][self.player_x] = Map.THIN_ICE.value
            self.current_tiles += 1

        self.player_x = new_x
        self.player_y = new_y
        self.current_points += 1

        self.check_coin_bag()