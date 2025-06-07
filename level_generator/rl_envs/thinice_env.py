# thinice_env
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random
from collections import deque
from src.mapping import Map
from src.levels import encode_levels_to_txt, Level


class ThinIcePhaseGenEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.height = 15
        self.width = 19
        self.max_steps = 200

        # Tipos de blocos possíveis para gerar
        self.tiles = [Map.WATER.value, Map.WALL.value, Map.THIN_ICE.value, Map.THICK_ICE.value]

        # Ações: 0=up, 1=down, 2=left, 3=right, 4=set THIN, 5=set THICK, 6=set WATER, 7=set WALL
        self.action_space = spaces.Discrete(8)

        # Observação: grid + posição da tartaruga
        self.observation_space = spaces.Dict({
            "grid": spaces.Box(low=0, high=9, shape=(self.height, self.width), dtype=np.int32),
            "pos": spaces.Box(low=0, high=max(self.width, self.height), shape=(2,), dtype=np.int32)
        })

        self.reset()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.grid = np.full((self.height, self.width), Map.WATER.value, dtype=np.int32)
        self.pos = [random.randint(0, self.height - 1), random.randint(0, self.width - 1)]
        self.steps = 0
        return self._get_obs(), {}

    def _get_obs(self):
        return {"grid": self.grid.copy(), "pos": np.array(self.pos, dtype=np.int32)}

    def step(self, action):
        r, c = self.pos
        self.steps += 1
        reward = 0
        terminated = False
        truncated = False

        if action == 0 and r > 0:
            self.pos[0] -= 1
        elif action == 1 and r < self.height - 1:
            self.pos[0] += 1
        elif action == 2 and c > 0:
            self.pos[1] -= 1
        elif action == 3 and c < self.width - 1:
            self.pos[1] += 1
        elif action in [4, 5, 6, 7]:
            tile = self.tiles[action - 4]
            self.grid[r, c] = tile
            reward = self._reward_local(r, c, tile)

        if self.steps >= self.max_steps:
            terminated = True
            reward += self._final_reward()

        return self._get_obs(), reward, terminated, truncated, {}

    def _reward_local(self, r, c, tile):
        reward = 0
        if tile in [Map.THIN_ICE.value, Map.THICK_ICE.value]:
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    if self.grid[nr, nc] in [Map.THIN_ICE.value, Map.THICK_ICE.value]:
                        reward += 0.1
        return reward

    def _final_reward(self):
        total_thin = np.sum(self.grid == Map.THIN_ICE.value)
        total_thick = np.sum(self.grid == Map.THICK_ICE.value)
        total_weighted = total_thin + 2 * total_thick

        if total_weighted == 0:
            return -1.0

        visited = set()
        queue = deque([tuple(self.pos)])
        covered_weight = 0

        while queue:
            r, c = queue.popleft()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            current = self.grid[r, c]
            if current == Map.THIN_ICE.value:
                covered_weight += 1
            elif current == Map.THICK_ICE.value:
                covered_weight += 2
            else:
                continue
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    if self.grid[nr, nc] in [Map.THIN_ICE.value, Map.THICK_ICE.value] and (nr, nc) not in visited:
                        queue.append((nr, nc))

        ratio = covered_weight / total_weighted
        if ratio < 0.5:
            return -0.5 + ratio
        return ratio

    def render(self):
        chars = {
            Map.WATER.value: '~',
            Map.WALL.value: '#',
            Map.THIN_ICE.value: '.',
            Map.THICK_ICE.value: '=',
        }
        print("\n".join(
            "".join(chars.get(cell, '?') for cell in row)
            for row in self.grid
        ))

    def save_level(self, path):
        start = tuple(self.pos[::-1])
        level = Level(grid=self.grid.tolist(), start=start, coin_bags=[], keys=[], blocks=[], teleports=[])
        encode_levels_to_txt(level, path)
