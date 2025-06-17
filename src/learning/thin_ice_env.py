import gymnasium as gym
from gymnasium import spaces
import numpy as np
from src.levels import Level
from src.game import Game
from src.mapping import Map
from src.levels import Level
from collections import deque

LEVELS_FOLDER = 'original_game'

class ThinIceEnv(gym.Env):
    def __init__(self):
        super(ThinIceEnv, self).__init__()

        # Actions: 0=up, 1=down, 2=left, 3=right
        self.action_space = spaces.Discrete(4)

        # 0 - Standard tiles
        # 1 - Thin Ice
        # 2 - Thick Ice
        # 3 - Locks and keys
        # 4 - Player
        # 5 - Pushable blocks
        # 6 - Coin bags
        # 7 - Teleports
        # 8 - Level finish
        # 9 - Walls and water
        self.obs_shape = (10, 15, 19)
        self.observation_space = spaces.Box(low=0, high=1, shape=self.obs_shape, dtype=np.uint8)
        self.points = 0
        self.level_folder = 'original_game'
        self.level_index = 0
        self.seed = 42

        self.reset()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        level = Level(LEVELS_FOLDER, 0)
        print(level)
        self.game = Game(
                        level = level,
                        perfect_score_required = False,
                    )
        self.visited = set()
        return self._get_obs(), {}


    def step(self, action):
        direction = [(0, -1), (0, 1), (-1, 0), (1, 0)][action]

        self.game.move_player(direction)

        moving_block, block_direction = self.game.block_mov
        while moving_block != None:
            self.game.move_block(moving_block, block_direction)

        self.game.check_progress()

        obs = self._get_obs()
        reward = self._compute_reward()

        if (self.game.level.current_level_id, self.game.player_x, self.game.player_y) not in self.visited:
            self.visited.add((self.game.level.current_level_id, self.game.player_x, self.game.player_y))

        done = self._is_done()
        info = {}

        return obs, reward, done, False, info

    def _is_done(self):
        tile = self.game.level.grid[self.game.player_y][self.game.player_x]
        return tile == Map.FINISH.value and self.game.level.current_level_id == 36

    def _compute_reward(self):
        reward = 0
        diff = self.game.current_points - self.points
        self.points = self.game.current_points
        if not self.all_ice_reachable():
            reward -= 10
        if diff > 0:
            reward += diff if diff < 100 else diff + 0.5
        elif (self.game.player_x, self.game.player_y) == self.game.level.start:
            reward -= 100
        else:
            reward -= 0.5
        if (self.game.player_x, self.game.player_y) not in self.visited:
            reward += 0.1
        if self.game.level.grid[self.game.player_y][self.game.player_x] == Map.FINISH.value:
            reward += 50
        return reward

    def _get_obs(self):
        grid = self.game.level.grid
        obs = np.zeros(self.obs_shape, dtype=np.uint8)

        for y in range(15):
            for x in range(19):
                tile = grid[y][x]
                if tile == Map.TILE.value:
                    obs[0, y, x] = 1
                elif tile == Map.THIN_ICE.value:
                    obs[1, y, x] = 1
                elif tile == Map.THICK_ICE.value:
                    obs[2, y, x] = 1
                elif tile == Map.LOCK.value:
                    obs[3, y, x] = 1
                elif tile == Map.FINISH.value:
                    obs[8, y, x] = 1
                elif tile in (Map.WALL.value, Map.WATER.value):
                    obs[9, y, x] = 1

        obs[4, self.game.player_y, self.game.player_x] = 1

        for block in self.game.level.blocks:
            obs[5, block[1], block[0]] = 1

        for key in self.game.level.keys:
            obs[3, key[1], key[0]] = 1

        for coin in self.game.level.coin_bags:
            obs[6, coin[1], coin[0]] = 1

        for teleport in self.game.level.teleports:
            obs[7, teleport[1], teleport[0]] = 1

        return obs
    
    def action_masks(self):
        mask = np.ones(4, dtype=bool)
        for i, (dx, dy) in enumerate([(0, -1), (0, 1), (-1, 0), (1, 0)]):
            nx, ny = self.game.player_x + dx, self.game.player_y + dy
            if not self._valid_move(nx, ny):
                mask[i] = False
        return mask
    
    def _valid_move(self, x, y):
        return (0 <= x < 19 and 0 <= y < 15 and self.game.level.grid[y][x] not in [Map.WALL.value, Map.WATER.value])
        
    def all_ice_reachable(self):
        grid = self.game.level.grid
        height = len(grid)
        width = len(grid[0])
        visited = [[False for _ in range(width)] for _ in range(height)]
        ice_tiles = set()
        reachable_ice = set()

        # Map teleport pairs (assumes bidirectional pairing)
        teleport_map = {}
        teleports = self.game.level.teleports
        if len(teleports) % 2 == 0:
            for i in range(0, len(teleports), 2):
                a = teleports[i]
                b = teleports[i + 1]
                teleport_map[a] = b
                teleport_map[b] = a

        # Identify all ice tile positions
        for y in range(height):
            for x in range(width):
                tile = grid[y][x]
                if tile in (Map.THIN_ICE.value, Map.THICK_ICE.value):
                    ice_tiles.add((x, y))

        # BFS from player's current position
        queue = deque()
        queue.append((self.game.player_x, self.game.player_y))
        visited[self.game.player_y][self.game.player_x] = True

        while queue:
            x, y = queue.popleft()

            if (x, y) in ice_tiles:
                reachable_ice.add((x, y))

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                    tile = grid[ny][nx]
                    if tile not in (Map.WALL.value, Map.WATER.value):
                        visited[ny][nx] = True
                        queue.append((nx, ny))

            # Handle teleportation
            if (x, y) in teleport_map:
                tx, ty = teleport_map[(x, y)]
                if not visited[ty][tx]:
                    visited[ty][tx] = True
                    queue.append((tx, ty))

        return reachable_ice == ice_tiles
    