# src/env/thin_ice_env.py

import gymnasium as gym
import numpy as np
from pygame import display
from src.game import Game
from src.levels import get_level
from src.mapping import Map

class ThinIceEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"]}

    ACTIONS = np.array([(0,-1), (1,0), (0,1), (-1,0)])  # U,R,D,L

    def __init__(self, level_index=None, level_folder="original_game", max_steps=300, render_mode=None):
        super().__init__()
        self.level_index = level_index
        self.level_folder = level_folder
        self.max_steps = max_steps
        self.render_mode = render_mode

        C, H, W = len(Map), 15, 19
        self.observation_space = gym.spaces.Box(0, 1, (C, H, W), np.float32)
        self.action_space = gym.spaces.Discrete(len(self.ACTIONS))
        
    def _init_game(self):
        if self.level_index is None:
            self.level_index = np.random.choice([0, 1, 2])  # aleatoriedade
        level = get_level(self.level_folder, self.level_index)
        self.game = Game(self.level_index, level,
                         level.start[0], level.start[1],
                         points=0, current_points=0,
                         keys_obtained=0, current_tiles=0,
                         solved=0, block_mov=(None,(0,0)))
        self.visited = set()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._init_game()
        self.step_count = 0
        obs = self._get_obs()
        info = {"action_mask": self._legal_mask()}
        return obs, info

    def step(self, action: int):
        """Aplica a ação, calcula recompensas e devolve (obs, reward, done, truncated, info)."""

        # ---------- 1. Executa ação ----------
        self.step_count += 1
        dx, dy = type(self).ACTIONS[action]

        prev_x, prev_y          = self.game.player_x, self.game.player_y
        prev_points             = self.game.current_points
        prev_tiles              = self.game.current_tiles

        self.game.move_player((dx, dy))
        new_pos   = (self.game.player_x, self.game.player_y)
        invalid   = (prev_x, prev_y) == new_pos               # não saiu do lugar?

        # ---------- 2. Recompensas imediatas ----------
        reward = 0.0 if invalid else -0.01                    # custo do passo
        if not invalid and new_pos not in self.visited:       # explorou tile novo
            reward += 0.05
            self.visited.add(new_pos)

        # coleta de moedas / tiles (diferença desde último step)
        if self.game.current_points > prev_points:
            reward += (self.game.current_points - prev_points) * 0.01
        if self.game.current_tiles  > prev_tiles:
            reward += 0.01

        # ---------- 3. Verifica término ou travamento ----------
        done = False
        if self.game.check_next_level(self.level_folder):     # fase concluída
            # ———— parâmetros da fórmula —
            FINISH_BASE   = 1.0   # a
            PERFECT_BONUS = 1.0   # -b  (b = -1  → +1 se perfeito)
            PENALTY_W     = 2.0   # c/d

            total_pts   = self.game.level.total_points
            current_pts = self.game.current_points
            miss_ratio  = 0 if total_pts == 0 else (total_pts - current_pts) / total_pts

            total_tiles = self.game.level.total_tiles
            miss_tiles  = (total_tiles - self.game.current_tiles) / total_tiles

            perfect = (miss_ratio == 0) and (miss_tiles == 0)

            # ———— aplica fórmula —
            reward += FINISH_BASE
            if perfect:
                reward += PERFECT_BONUS
            reward -= miss_ratio * PENALTY_W   # só moedas; inclua +miss_tiles*… se quiser penalizar tiles também

            self.level_index = self.game.num_level
            print(f"→ Avançou para o nível {self.level_index}")
            done = True

        elif self._stuck():
            reward -= 1.0      # encurralado
            done = True

        # ---------- 4. Truncamento por passo máximo ----------
        truncated = self.step_count >= self.max_steps
        info = {"invalid": invalid, "action_mask": self._legal_mask()}

        return self._get_obs(), reward, done, truncated, info

    def _get_obs(self):
        H, W = 15, 19
        tensor = np.zeros((len(Map), H, W), dtype=np.float32)
        for y, row in enumerate(self.game.level.grid):
            for x, val in enumerate(row):
                tensor[val, y, x] = 1
        tensor[Map.EMPTY.value, self.game.player_y, self.game.player_x] = 0
        tensor[0, self.game.player_y, self.game.player_x] = 1
        return tensor

    def _inside(self, x, y):
        return 0 <= x < 19 and 0 <= y < 15

    def _legal_mask(self):
        mask = []
        for dx, dy in type(self).ACTIONS:
            nx, ny = self.game.player_x + dx, self.game.player_y + dy
            legal = self._inside(nx, ny) and \
                    self.game.level.grid[ny][nx] not in (Map.WALL.value,
                                                         Map.WATER.value,
                                                         Map.LOCK.value)
            mask.append(legal)
        return np.array(mask, dtype=bool)

    def _stuck(self):
        return not self._legal_mask().any()

    def render(self, mode="human"):
        if mode == "rgb_array":
            return pygame.surfarray.array3d(display.get_surface()).transpose(1, 0, 2)
        if mode == "human":
            from src.main import draw_screen  # 👈 função que redesenha a tela
            draw_screen(self.game)            # 👈 chama a renderização visual
            pygame.display.flip()
            pygame.time.wait(80)  # espera ~80ms entre frames (12.5 FPS)

    def _ascii_render(self):
        inv = {v.value: k for k, v in Map.__members__.items()}
        for j, row in enumerate(self.game.level.grid):
            line = ""
            for i, val in enumerate(row):
                if (i, j) == (self.game.player_x, self.game.player_y):
                    line += "A"
                else:
                    line += str(inv[val])
            print(line)
        print()
        
    def change_level_folder(self, new_folder):
        self.level_folder = new_folder