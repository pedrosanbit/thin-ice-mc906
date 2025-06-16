# src/env/thin_ice_env.py
import gymnasium as gym
import numpy as np
from pygame import display
from pathlib import Path

from src.game import Game, Mode
from src.level_set import LevelSet, Progression       # ⬅️ NOVO
from src.mapping import Map


class ThinIceEnv(gym.Env):
    """Ambiente Gymnasium para o Thin Ice compatível com o novo LevelSet."""

    metadata = {"render_modes": ["human", "rgb_array"]}
    ACTIONS = np.array([(0, -1), (1, 0), (0, 1), (-1, 0)])  # U, R, D, L

    # -------------------------------------------------- #
    # 1. Construtor                                      #
    # -------------------------------------------------- #
    def __init__(
        self,
        level_set: LevelSet | None = None,
        *,
        folder: str = "original_game",
        max_index: int | None = None,
        progression: Progression = Progression.SEQUENTIAL,
        start_index: int | None = None,
        max_steps: int = 300,
        render_mode: str | None = None,
    ):
        super().__init__()

        # cria LevelSet se o chamador não passou um pronto
        if level_set is None:
            # se max_index não foi informado, deduz pelo nº de arquivos
            if max_index is None:
                base_dir = Path(__file__).resolve().parent.parent / "data" / "levels" / folder
                max_index = max(
                    int(p.stem.split("_")[1]) for p in base_dir.glob("level_*.txt")
                )
            level_set = LevelSet(folder, max_index, progression=progression)

        self.level_set   = level_set
        self.level_index = start_index
        self.max_steps   = max_steps
        self.render_mode = render_mode

        probe_idx = start_index if start_index is not None else 0
        probe_level = self.level_set.get_level(start_index or 0)
        g = probe_level.grid
        C, H, W = len(Map) + 2, g.height, g.width       # +2 p/ CoordConv

        self.observation_space = gym.spaces.Box(0, 1, (C, H, W), np.float32)
        self.action_space      = gym.spaces.Discrete(len(self.ACTIONS))
    # -------------------------------------------------- #
    # 2. Inicialização de jogo                           #
    # -------------------------------------------------- #
    def _init_game(self):
        if self.level_index is None:
            # escolhe aleatoriamente um índice válido
            self.level_index = self.np_random.integers(len(self.level_set))
        self.game = Game(self.level_set, start_index=self.level_index, mode=Mode.RESTRICTED)
        self.visited = { (self.game.player_x, self.game.player_y) }

    # -------------------------------------------------- #
    # 3. API Gymnasium                                   #
    # -------------------------------------------------- #
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._init_game()
        self.step_count = 0
        obs  = self._get_obs()
        info = {"action_mask": self._legal_mask()}
        return obs, info

    def step(self, action: int):
        # 1. aplica ação
        self.step_count += 1
        dx, dy = type(self).ACTIONS[action]

        prev_x, prev_y      = self.game.player_x, self.game.player_y
        prev_points         = self.game.current_points
        prev_tiles          = self.game.current_tiles

        self.game.move_player((dx, dy))
        new_pos = (self.game.player_x, self.game.player_y)
        invalid = (prev_x, prev_y) == new_pos

        # 2. recompensas básicas
        reward = 0.0 if invalid else -0.01
        if not invalid and new_pos not in self.visited:
            reward += 0.05
            self.visited.add(new_pos)

        if self.game.current_points > prev_points:
            reward += (self.game.current_points - prev_points) * 0.01
        if self.game.current_tiles > prev_tiles:
            reward += 0.01

        # 3. término da fase ou encurralado
        done = False


        # Chegou ao FINISH?
        advanced = False
        advanced = False
        if self.game.level.grid.tile(self.game.player_x, self.game.player_y) is Map.FINISH:
            # ---------- parâmetros ----------
            FINISH_BASE   = 1.0
            PERFECT_BONUS = 1.0
            PENALTY_W     = 2.0

            total_pts   = self.game.level.total_points
            current_pts = self.game.current_points

            # razão de pontos (0‥1)
            points_ratio = 0.0 if total_pts == 0 else current_pts / total_pts
            miss_ratio   = 1.0 - points_ratio

            perfect = (miss_ratio == 0.0)

            # ---------- avança de fase ----------
            advanced, _ = self.game.check_finish()   # carrega próximo nível (se existir)

            # recompensa base + bônus/perda
            reward += FINISH_BASE
            if perfect:
                reward += PERFECT_BONUS
            reward -= miss_ratio * PENALTY_W

            self.level_index = self.game.num_level
            print(f"→ Avançou para o nível {self.level_index}")
            done = True

        elif self._stuck():
            reward -= 1.0      # encurralado
            done = True

        # ---------- 4. Truncamento por passo máximo ----------
        truncated = self.step_count >= self.max_steps
        info = {
            "invalid": invalid,
            "action_mask": self._legal_mask(),
            "advanced": advanced,
            "points_ratio": points_ratio if advanced else 0.0,
        }
        return self._get_obs(), reward, done, truncated, info

    def _stuck(self) -> bool:
        """Retorna True se o jogador não tem movimentos válidos."""
        return not self._legal_mask().any()
    # -------------------------------------------------- #
    # 4. Observação, máscara e utilitários               #
    # -------------------------------------------------- #
    def _get_obs(self):
        g = self.game.level.grid
        H, W = g.height, g.width

        # ---- (len(Map) + 2) canais ----------------------------------------
        tensor = np.zeros((len(Map) + 2, H, W), dtype=np.float32)

        # one-hot dos tiles
        for x, y, tile in g.iter_coords():
            tensor[tile.value, y, x] = 1

        # canal 0 = posição do jogador
        tensor[Map.EMPTY.value, self.game.player_y, self.game.player_x] = 0
        tensor[0, self.game.player_y, self.game.player_x] = 1

        # ---- CoordConv: posição absoluta normalizada ----------------------
        xs = np.linspace(0, 1, W, dtype=np.float32)
        ys = np.linspace(0, 1, H, dtype=np.float32)
        tensor[-2, :, :] = xs            # X-coord (repetido em cada linha)
        tensor[-1, :, :] = ys[:, None]   # Y-coord (repetido em cada coluna)

        return tensor


    def _inside(self, x, y):
        return self.game.level.grid.inside(x, y)

    def _legal_mask(self):
        mask = []
        g = self.game.level.grid
        blocks = set(self.game.level.blocks)
        for (dx, dy) in type(self).ACTIONS:
            nx, ny = self.game.player_x + dx, self.game.player_y + dy

            # 1. Fora dos limites?
            if not g.inside(nx, ny):
                mask.append(False)
                continue

            tile = g.tile(nx, ny)

            # 2. Parede/água?
            if tile in {Map.WALL, Map.WATER}:
                mask.append(False)
                continue

            # 3. Tranca sem chave?
            if tile is Map.LOCK and self.game.keys_obtained == 0:
                mask.append(False)
                continue

            # 4. Bloco empurrável – verifica espaço livre/teleporte no destino
            if (nx, ny) in blocks:
                bx, by = nx + dx, ny + dy            # destino do bloco
                if (
                    not g.inside(bx, by)
                    or g.tile(bx, by) in {Map.WALL, Map.WATER, Map.LOCK}
                    or (bx, by) in blocks
                ):
                    mask.append(False)
                    continue

            # 5. Ação é segura
            mask.append(True)

        return np.array(mask, dtype=bool)


    # -------------------------------------------------- #
    # 5. Renderização                                    #
    # -------------------------------------------------- #
    def render(self, mode="human"):
        if mode == "rgb_array":
            import pygame  # import tardio
            return pygame.surfarray.array3d(display.get_surface()).transpose(1, 0, 2)
        if mode == "human":
            from src.main import draw_screen
            import pygame
            draw_screen(self.game)
            pygame.display.flip()
            pygame.time.wait(80)

    def _ascii_render(self):
        inv = {v.value: k for k, v in Map.__members__.items()}
        g   = self.game.level.grid

        for y in range(g.height):
            line = "".join(
                "A" if (x, y) == (self.game.player_x, self.game.player_y)
                else str(inv[g.tile(x, y).value])
                for x in range(g.width)
            )
            print(line)
        print()

