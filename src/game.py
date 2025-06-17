# /src/game.py


from src.levels import Level
from src.mapping import Map

class Game:
    def __init__(
            self, 
            level, 
            perfect_score_required = False,
            points = 0, 
            current_points = 0, 
            solved = 0,
            seed=42
        ):


        self.level = level

        self.perfect_score_required = perfect_score_required
        self.points = points
        self.current_points = current_points
        self.solved = solved

        #self.current_tiles = 0
        #self.player_x = self.level.start[0]
        #self.player_y = self.level.start[1]
        #self.keys_obtained = 0
        #self.block_mov = (None, (0, 0))
        self.reload_level()

        self.seed = seed

    def _in_bounds(self, x: int, y: int) -> bool:
        rows = len(self.level.grid)
        cols = len(self.level.grid[0])
        return 0 <= x < cols and 0 <= y < rows
    
    def load_new_level_variables(self):
        self.current_tiles = 0
        self.current_points = self.points
        self.player_x = self.level.start[0]
        self.player_y = self.level.start[1]
        self.keys_obtained = 0
        self.block_mov = (None, (0, 0))
        
    def load_next_level(self):
        self.current_points += self.current_tiles * 2
        self.points = self.current_points

        self.solved += 1
        
        self.level.load_next_level()
        self.load_new_level_variables()

    def reload_level(self):
        self.level.reload_level()
        self.load_new_level_variables()


    def check_progress(self):
        rows = len(self.level.grid)
        cols = len(self.level.grid[0])

        # Verifica se o jogador chegou ao ponto final

        if self.level.grid[self.player_y][self.player_x] == Map.FINISH.value:
            # Caso perfeito, verifica se todos os tiles foram coletados
            if self.perfect_score_required:
                if self.current_tiles == self.level.total_tiles:
                    self.load_next_level()

                    return "SUCCESS", 1.0  # Passou com sucesso (perfeito)
                else:
                    # Não conseguiu coletar todos os tiles, reinicia a fase
                    ratio = float(self.current_tiles) / self.level.total_tiles
                    self.reload_level()
                    return "NOT_SUFFICIENT", ratio  # Passou sem sucesso

            # Caso não precise do perfeito, só checa o avanço
            self.load_next_level()

            return "SUCCESS", 1.0  # Passou normalmente

        # Verifica se o jogador ficou sem movimentos válidos (Game Over)
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]
        for dr, dc in directions:
            nr, nc = self.player_y + dr, self.player_x + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                # Lock is openable
                if self.level.grid[nr][nc] == Map.LOCK.value and self.keys_obtained > 0:
                    return "CONTINUE", 0
                # Walkable tile available
                if self.level.grid[nr][nc] not in (Map.WALL.value, Map.WATER.value, Map.LOCK.value) and (nc, nr) not in self.level.blocks:
                    return "CONTINUE", 0
                # Block is pushable
                if (nc, nr) in self.level.blocks and self.level.grid[nr + dr][nc + dc] not in (Map.WALL.value, Map.WATER.value, Map.LOCK.value):
                    return "CONTINUE", 0

        # Caso não tenha movimentos válidos, game over
        self.reload_level()
        return "GAME_OVER", 0  

    def check_coin_bag(self):
        for coin_bag in self.level.coin_bags:
            if self.player_x == coin_bag[0] and self.player_y == coin_bag[1]:
                self.current_points += 100
                self.level.coin_bags.remove(coin_bag)
                return
    
    def check_key(self):
        for key in self.level.keys:
            if self.player_x == key[0] and self.player_y == key[1]:
                self.keys_obtained += 1
                self.level.keys.remove(key)
                return
            
    def check_lock(self, x, y):
        rows = len(self.level.grid)
        cols = len(self.level.grid[0])
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]
        for dr, dc in directions:
            nr, nc = y + dr, x + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if self.level.grid[nr][nc] == Map.LOCK.value and self.keys_obtained > 0:
                    self.keys_obtained -= 1
                    self.level.grid[nr][nc] = Map.THIN_ICE.value

    def move_block(self, block, direction):
        new_x = block[0] + direction[0]
        new_y = block[1] + direction[1]

        if self.level.grid[new_y][new_x] in (Map.WALL.value, Map.LOCK.value, Map.WATER.value):
            self.block_mov = (None, (0,0))
            return
        
        if self.level.grid[new_y][new_x] == Map.TELEPORT.value:
            new_x, new_y = self.level.teleports[1 - self.level.teleports.index((new_x, new_y))]
        
        self.level.blocks.remove(block)
        self.level.blocks.append((new_x, new_y))
        self.block_mov = ((new_x, new_y), direction)


    def move_player(self, direction):
        new_x = self.player_x + direction[0]
        new_y = self.player_y + direction[1]

        # ---------- Limites do grid ----------
        if not self._in_bounds(new_x, new_y):
            return                       

        if self.level.grid[new_y][new_x] in (Map.WALL.value, Map.LOCK.value, Map.WATER.value):
            return
        
        if self.level.grid[new_y][new_x] == Map.TELEPORT.value:
            new_x, new_y = self.level.teleports[1 - self.level.teleports.index((new_x, new_y))]
            for teleport in self.level.teleports:
                self.level.grid[teleport[1]][teleport[0]] = Map.TILE.value
            self.player_x = new_x
            self.player_y = new_y
        
        if (new_x, new_y) in (self.level.blocks):
            if self.level.grid[new_y + direction[1]][new_x + direction[0]] in (Map.WALL.value, Map.WATER.value, Map.LOCK.value):
                return
            self.block_mov = ((new_x, new_y), direction)
            self.move_block(self.block_mov[0], direction)

        current_tile = self.level.grid[self.player_y][self.player_x]
        if current_tile == Map.THIN_ICE.value:
            self.level.grid[self.player_y][self.player_x] = Map.WATER.value
        elif current_tile == Map.THICK_ICE.value:
            self.level.grid[self.player_y][self.player_x] = Map.THIN_ICE.value

        self.check_lock(new_x, new_y)

        if self.level.grid[new_y][new_x] == Map.TELEPORT.value:
            new_x, new_y = self.level.teleports[1 - self.level.teleports.index((new_x, new_y))]
            for teleport in self.level.teleports:
                self.level.grid[teleport[1]][teleport[0]] = Map.TILE.value

        self.player_x = new_x
        self.player_y = new_y
        self.current_points += 1
        self.current_tiles += 1

        self.check_coin_bag()
        self.check_key()