import random

from src.mapping import Map
from src.mapping import GRID_HEIGHT, GRID_WIDTH, CELL_SIZE

def add_coin(self):
    if not self.coin_placed and self.is_valid_tile():
        self.coin_bags.append((self.player_x, self.player_y))
        self.coin_placed = True

def add_key(self):
    if not self.key_placed and self.is_valid_tile():
        self.keys.append((self.player_x, self.player_y))
        self.key_placed = True
        print("[i] Chave colocada.")

def add_lock(self):
    if not self.key_placed or self.lock_placed: return
    if not self.is_valid_tile(exclude_start=True): return
    if (self.player_x, self.player_y) in self.keys: return
    tile = self.grid[self.player_y][self.player_x]
    if tile != Map.THIN_ICE.value: return

    wall_count = sum([
        self.grid[self.player_y + dy][self.player_x + dx] == Map.WALL.value
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]
        if 0 <= self.player_x + dx < GRID_WIDTH and 0 <= self.player_y + dy < GRID_HEIGHT
    ])
    if wall_count != 3: return
    if (self.player_x, self.player_y) in self.coin_bags + self.teleports + self.keys: return

    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = self.player_x + dx, self.player_y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
            if self.grid[ny][nx] != Map.WALL.value:
                self.grid[ny][nx] = Map.THIN_ICE.value

    self.grid[self.player_y][self.player_x] = Map.LOCK.value
    self.lock_placed = True
    self._mark_forbidden_area()
    print("[i] Tranca colocada.")

def add_exit_point(self):
    if not self.is_valid_finish_tile():
        print("[!] Tile inválido para ponto final.")
        return False

    if self.key_placed and not self.lock_placed:
        print("[!] Há uma chave no mapa, mas nenhuma tranca foi colocada.")
        return False

    self.grid[self.player_y][self.player_x] = Map.FINISH.value
    print("[✓] Ponto final definido.")
    self.save_level()
    return True