# /src/env/thin_ice_env.py

import gymnasium as gym
import numpy as np
import pygame
from src.game import Game
from src.levels import Level
from src.mapping import Map

class ThinIceEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"]}

    ACTIONS = np.array([(0, -1), (1, 0), (0, 1), (-1, 0)])  # U, R, D, L

    def __init__(self, level_folder="original_game", level_index=0, max_steps=300, render_mode=None, seed=42, allow_failure_progression=False):
        super().__init__()
        self.level_index = level_index
        self.level_folder = level_folder
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.seed = seed
        self.allow_failure_progression = allow_failure_progression

        # Define os espaços de observação e ação esperados pelo Gymnasium
        C, H, W = len(Map), 15, 19
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(C, H, W), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(4)


    def _init_game(self):
        if not hasattr(self, "game"):
            initial_level = Level(
                self.level_folder,
                loop_on_finish=True,
                current_level_id=self.level_index
            )
            self.game = Game(
                initial_level,
                perfect_score_required=True,
                points=0,
                current_points=0,
                solved=0,
                seed=self.seed
            )
        else:
            self.game.reload_level()
        self.visited = set()


    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._init_game()
        self.step_count = 0
        obs = self._get_obs()
        info = {"action_mask": self._legal_mask()}
        return obs, info
    
    def step(self, action: int):
        self.step_count += 1
        dx, dy = type(self).ACTIONS[action]
        prev_x, prev_y = self.game.player_x, self.game.player_y
        prev_tiles = self.game.current_tiles

        self.game.move_player((dx, dy))
        new_pos = (self.game.player_x, self.game.player_y)
        invalid = (prev_x, prev_y) == new_pos

        reward = -0.2 if invalid else -0.01 # penalidade leve por passo inválido

        # 👇 Bonificação por explorar novo tile
        if not invalid and new_pos not in self.visited:
            self.visited.add(new_pos)
            reward += 0.01

        # Recompensa por derretimento de blocos
        if self.game.current_tiles > prev_tiles:
            reward += (self.game.current_tiles - prev_tiles) * 0.1

        done = False
        result, score_ratio = self.game.check_progress()

        if result == "SUCCESS":
            reward += 1.0
            done = True
        elif result == "NOT_SUFFICIENT":
            reward -= 0.1 * (1 - score_ratio)
            done = True
        elif result == "GAME_OVER":
            reward -= 0.5 + (1 - score_ratio)
            done = True

        truncated = self.step_count >= self.max_steps

        info = {
            "invalid": invalid,
            "action_mask": self._legal_mask(),
            "score_ratio": score_ratio,
            "result": result,
            "level_id": self.game.level.current_level_id
        }

        if (done or truncated) and self.allow_failure_progression:
            self.game.load_next_level()

        #if self.game.level.total_tiles > 20:
        #    reward += np.random.normal(0, 0.01)  # média 0, desvio 0.01

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
            return pygame.surfarray.array3d(pygame.display.get_surface()).transpose(1, 0, 2)
        if mode == "human":
            from old.main import draw_screen  # 👈 função que redesenha a tela
            draw_screen(self.game)  # 👈 chama a renderização visual
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

    def change_level_folder(self, new_folder, level_index = 0):
        self.level_folder = new_folder
        self.level_index = level_index