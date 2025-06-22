# src/level_creator.py

import pygame
import random
from collections import deque

from src.mapping import Map, get_color
from src.levels import encode_levels_to_txt
from src.utils import init_screen
import os

GRID_HEIGHT = 15
GRID_WIDTH = 19
CELL_SIZE = 32

class LevelCreator:
    def __init__(self):
        self.screen, self.font = init_screen()
        self.grid = [[Map.WALL.value for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.start = self._get_random_start()
        self.grid[self.start[1]][self.start[0]] = Map.THIN_ICE.value
        self.player_x, self.player_y = self.start
        self.forbidden_area = set()
        self.original_start = self.start

        self.coin_bags = []
        self.keys = []
        self.locks = []
        self.teleports = []
        self.teleport_stage = 0
        self.teleport_temp = None
        self.lock_placed = False
        self.coin_placed = False
        self.key_placed = False

    def _mark_forbidden_area(self):
        visited = set()
        queue = deque([self.original_start])
        forbidden = set()

        while queue:
            x, y = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            forbidden.add((x, y))

            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    tile = self.grid[ny][nx]
                    if tile in (Map.THIN_ICE.value, Map.THICK_ICE.value):
                        if (nx, ny) not in visited:
                            queue.append((nx, ny))
                    elif tile == Map.WALL.value:
                        forbidden.add((nx, ny))

        self.forbidden_area = forbidden

    def _get_random_start(self):
        x = random.randint(1, GRID_WIDTH - 2)
        y = random.randint(1, GRID_HEIGHT - 2)
        return (x, y)

    def draw(self):
        self.screen.fill((218, 240, 255))

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(
                    self.screen,
                    get_color(self.grid[y][x]),
                    (x * CELL_SIZE, (y + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )

        for cx, cy in self.coin_bags:
            pygame.draw.circle(self.screen, get_color(Map.COIN_BAG.value),
                               (cx * CELL_SIZE + CELL_SIZE // 2, (cy + 1) * CELL_SIZE + CELL_SIZE // 2),
                               CELL_SIZE // 3)

        for kx, ky in self.keys:
            pygame.draw.circle(self.screen, get_color(Map.LOCK.value),
                               (kx * CELL_SIZE + CELL_SIZE // 2, (ky + 1) * CELL_SIZE + CELL_SIZE // 2),
                               CELL_SIZE // 3)

        for tx, ty in self.teleports:
            pygame.draw.circle(self.screen, (200, 0, 255),
                               (tx * CELL_SIZE + CELL_SIZE // 2, (ty + 1) * CELL_SIZE + CELL_SIZE // 2),
                               CELL_SIZE // 3)


        pygame.draw.rect(self.screen, (255, 0, 0),
                         (self.player_x * CELL_SIZE, (self.player_y + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.flip()

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_UP]: dy = -1
            elif keys[pygame.K_DOWN]: dy = 1
            elif keys[pygame.K_LEFT]: dx = -1
            elif keys[pygame.K_RIGHT]: dx = 1
            if dx or dy:
                self.try_move(dx, dy)

            if keys[pygame.K_1]: self.add_coin()
            if keys[pygame.K_2]: self.add_key()
            if keys[pygame.K_3]: self.add_lock()
            if keys[pygame.K_4]: self.add_teleport()
            
            if keys[pygame.K_RETURN]:
                if not self.add_exit_point():
                    print("[i] Cancelando fase automaticamente.")
                    pygame.quit()
                    return
            if keys[pygame.K_ESCAPE]:
                print("[i] Fase descartada pelo usuário.")
                pygame.quit()
                return

            self.draw()

    def try_move(self, dx, dy):
        nx, ny = self.player_x + dx, self.player_y + dy
        if not (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT): return
        if (nx, ny) == self.original_start: return
        if (nx, ny) in self.forbidden_area: return

        current_val = self.grid[ny][nx]
        if current_val == Map.WALL.value:
            self.grid[ny][nx] = Map.THIN_ICE.value
        elif current_val == Map.THIN_ICE.value:
            self.grid[ny][nx] = Map.THICK_ICE.value
        elif current_val in (Map.THICK_ICE.value, Map.TELEPORT.value, Map.COIN_BAG.value, Map.LOCK.value):
            return
        self.player_x, self.player_y = nx, ny

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

    def add_teleport(self):
        if len(self.teleports) >= 2:
            print("[!] Apenas um par de teletransporte é permitido por fase.")
            return

        if self.teleport_stage == 0:
            if not self.is_valid_tile(exclude_start=True):
                print("[!] Tile inválido para entrada de teleporte.")
                return
            if self.is_tile_occupied(self.player_x, self.player_y):
                print("[!] Tile já contém item.")
                return
            if not self._has_valid_teleport_exit():
                print("[!] Nenhuma saída possível para o teleporte.")
                return

            self.teleport_temp = (self.player_x, self.player_y)
            self.teleport_stage = 1
            print("[i] Entrada do teleporte colocada.")
            return

        elif self.teleport_stage == 1:
            valid_walls = self._find_valid_teleport_exits()
            if not valid_walls:
                print("[!] Nenhuma parede válida para saída de teleporte.")
                self.teleport_temp = None
                self.teleport_stage = 0
                return

            exit_pos = random.choice(valid_walls)
            self.teleports.append(self.teleport_temp)
            self.teleports.append(exit_pos)

            tx1, ty1 = self.teleport_temp
            tx2, ty2 = exit_pos
            self.grid[ty1][tx1] = Map.TELEPORT.value
            self.grid[ty2][tx2] = Map.TELEPORT.value

            self.player_x, self.player_y = tx2, ty2
            self.teleport_temp = None
            self.teleport_stage = 0
            print("[✓] Teletransporte criado. Jogador movido para a saída.")

    def _has_valid_teleport_exit(self):
        return bool(self._find_valid_teleport_exits())

    def _find_valid_teleport_exits(self):
        valid = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] != Map.WALL.value:
                    continue
                adjacents = [(x + dx, y + dy) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]]
                valid_adj = sum(1 for ax, ay in adjacents
                                if 0 <= ax < GRID_WIDTH and 0 <= ay < GRID_HEIGHT and self.is_valid_tile_at(ax, ay))
                invalid_adj = sum(1 for ax, ay in adjacents
                                  if 0 <= ax < GRID_WIDTH and 0 <= ay < GRID_HEIGHT and (ax, ay) in self.forbidden_area)
                if valid_adj >= 1 and invalid_adj == 0:
                    valid.append((x, y))
        return valid

    def is_tile_occupied(self, x, y):
        return (x, y) in self.coin_bags + self.keys + self.locks + self.teleports

    def is_valid_tile(self, exclude_start=False):
        print("[DEBUG] Tile atual:", self.grid[self.player_y][self.player_x])
        #print("[DEBUG] É válido?", self.is_valid_tile(exclude_start=True))
        print("[DEBUG] Ocupado?", self.is_tile_occupied(self.player_x, self.player_y))
        print("[DEBUG] É o ponto inicial?", (self.player_x, self.player_y) == self.original_start)

        return self._is_valid_tile_general(self.player_x, self.player_y, exclude_start)

    def is_valid_tile_at(self, x, y):
        return self._is_valid_tile_general(x, y, exclude_start=(x, y) == self.original_start)

    def _is_valid_tile_general(self, x, y, exclude_start=False):
        if exclude_start and (x, y) == self.original_start:
            return False
        tile = self.grid[y][x]
        if tile != Map.THIN_ICE.value:
            return False
        if self.is_tile_occupied(x, y):
            return False
        return True

    
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

    def is_valid_finish_tile(self):
        """Verifica se o tile atual é um local válido para colocar o ponto final."""
        if (self.player_x, self.player_y) == self.original_start:
            return False
        if self.grid[self.player_y][self.player_x] != Map.THIN_ICE.value:
            return False
        if self.is_tile_occupied(self.player_x, self.player_y):
            return False
        return True
    
    def can_save_level(self):
        """Permite salvar se o jogador estiver em tile THIN_ICE ou FINISH, não for entrada e não estiver ocupado."""
        if (self.player_x, self.player_y) == self.original_start:
            return False
        if self.grid[self.player_y][self.player_x] not in (Map.THIN_ICE.value, Map.FINISH.value):
            return False
        if self.is_tile_occupied(self.player_x, self.player_y):
            return False
        return True


    def save_level(self):
        if not self.can_save_level():
            print("[!] Tile atual não é válido para salvar a fase.")
            return

        folder = "custom_created"
        os.makedirs(os.path.join("data", "levels", folder), exist_ok=True)
        index = len(os.listdir(os.path.join("data", "levels", folder)))
        total_tiles = sum([row.count(Map.THIN_ICE.value) for row in self.grid])
        encode_levels_to_txt(folder, index, self.grid, self.start, self.coin_bags, self.keys, [], self.teleports, total_tiles)
        print(f"[✓] Fase salva como level_{index:04}.txt")
        pygame.quit()

if __name__ == "__main__":
    LevelCreator().run()