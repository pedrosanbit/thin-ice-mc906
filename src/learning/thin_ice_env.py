import gymnasium as gym
from gymnasium import spaces
import numpy as np
from src.levels import get_level
from src.game import Game
from src.mapping import Map

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

        self.reset()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        level = get_level(0)
        self.game = Game(0, level, level.start[0], level.start[1], 0, 0, 0, 0, 0, (None, (0,0)))
        return self._get_obs(), {}

    def step(self, action):
        direction = [(0, -1), (0, 1), (-1, 0), (1, 0)][action]

        self.game.move_player(direction)

        moving_block, block_direction = self.game.block_mov
        while moving_block != None:
            self.game.move_block(moving_block, block_direction)

        next_level = self.game.check_next_level()
        if not next_level: self.game.check_game_over()

        obs = self._get_obs()
        reward = self._compute_reward()
        done = self._is_done()
        info = {}

        return obs, reward, done, False, info

    def _is_done(self):
        tile = self.game.level.grid[self.game.player_y][self.game.player_x]
        return tile == Map.FINISH.value and self.game.num_level == 36

    def _compute_reward(self):
        return self.game.current_points - self.points

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
