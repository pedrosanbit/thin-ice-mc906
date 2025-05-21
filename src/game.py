from levels import get_level
from mapping import Map

class Game:
    def __init__(self, level, grid, player_x, player_y, points, current_points, keys_obtained):
        self.level = level
        self.grid = grid
        self.player_x = player_x
        self.player_y = player_y
        self.points = points
        self.current_points = current_points
        self.keys_obtained = keys_obtained

    def load_level(self, num_level):
        level = get_level(num_level)
        self.grid = level.grid
        self.player_x = level.start[0]
        self.player_y = level.start[1]

    def check_next_level(self):
        if self.grid[self.player_y][self.player_x] == Map.FINISH.value:
            self.level += 1
            self.points = self.current_points
            self.load_level(self.level)
            return True
        return False
    
    def check_game_over(self):
        rows = len(self.grid)
        cols = len(self.grid[0])
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]
        for dr, dc in directions:
            nr, nc = self.player_y + dr, self.player_x + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if self.grid[nr][nc] not in (Map.WALL.value, Map.WATER.value):
                    return
        self.current_points = self.points
        self.load_level(self.level)

    def move_player(self, direction):
        new_x = self.player_x + direction[0]
        new_y = self.player_y + direction[1]

        if self.grid[new_y][new_x] in (Map.WALL.value, Map.WATER.value):
            return

        current_tile = self.grid[self.player_y][self.player_x]
        if current_tile == Map.THIN_ICE.value:
            self.grid[self.player_y][self.player_x] = Map.WATER.value
        elif current_tile == Map.THICK_ICE.value:
            self.grid[self.player_y][self.player_x] = Map.THIN_ICE.value

        self.player_x = new_x
        self.player_y = new_y
        self.current_points += 1

