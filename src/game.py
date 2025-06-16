from __future__ import annotations

import random
from enum import Enum
from typing import Optional, Tuple

from src.grid import Grid  # novo wrapper seguro
from src.levels import Level
from src.mapping import Map
from src.level_set import LevelSet, Progression  # wrapper de conjuntos de fases


class Mode(Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"  # deve coletar 100 % da pontuação


class Game:
    """Lógica do jogo + progressão controlada por *LevelSet*.

    Todos os acessos à matriz agora passam pelo wrapper :class:`Grid`.
    Isso elimina a repetição de verificações de limites e reduz o risco de
    `IndexError`.
    """

    MAX_LEVEL = 999  # mantido para compatibilidade

    # --------------------------------------------------
    # Inicialização
    # --------------------------------------------------
    def __init__(
        self,
        level_set: LevelSet,
        mode: Mode = Mode.NORMAL,
        *,
        start_index: int = 0,
    ) -> None:
        self.level_set = level_set
        self.mode = mode

        # Estado global
        self.num_level: int = start_index
        self.level: Level = self.level_set.get_level(start_index)
        self.player_x, self.player_y = self.level.start

        # Pontuação
        self.points: int = 0              # soma persistente
        self.current_points: int = 0      # durante fase corrente
        self._points_at_level_start: int = 0

        # Estatísticas auxiliares
        self.current_tiles: int = 0
        self.solved: int = 0

        # Inventário
        self.keys_obtained: int = 0
        # (bloco sendo movido, direcao)
        self.block_mov: Tuple[Optional[Tuple[int, int]], Tuple[int, int]] = (None, (0, 0))

    # --------------------------------------------------
    # Carregamento de fases
    # --------------------------------------------------
    def _load_level(self, idx: int) -> None:
        """Carrega *idx* e reseta contadores locais."""
        self.num_level = idx
        self.level = self.level_set.get_level(idx)

        self.player_x, self.player_y = self.level.start

        self._points_at_level_start = self.current_points
        self.current_tiles = 0
        self.keys_obtained = 0
        self.block_mov = (None, (0, 0))

    def reload_level(self) -> None:
        self._load_level(self.num_level)

    def load_next_level(self) -> bool:
        next_idx = self.level_set.next_index(self.num_level)
        if next_idx is None:
            return False  # jogo acabou (modo sequencial)
        self._load_level(next_idx)
        return True

    # --------------------------------------------------
    # Verificações de estado
    # --------------------------------------------------
    def check_finish(self) -> Tuple[bool, float]:
        """Verifica se o jogador está no FINISH.

        **Retorno:** `(avancou, ratio_perda)`
          * `avancou`: True se progrediu para o próximo nível.
          * `ratio_perda`: 0 se não houve perda ou modo NORMAL; caso RESTRICTED e
            falha, retorna `(pts_perdidos / total_pts_nivel)`.
        """
        if self.level.grid.tile(self.player_x, self.player_y) is not Map.FINISH:
            return False, 0.0

        # → jogador chegou ao FINISH
        total_pts_nivel = self.level.total_points
        pts_coletados = self.current_points - self._points_at_level_start
        coletou_tudo = pts_coletados >= total_pts_nivel

        if self.mode is Mode.NORMAL or coletou_tudo:
            # soma pontuação permanentemente
            self.points = self.current_points
            if coletou_tudo:
                self.solved += 1
            avancou = self.load_next_level()
            return avancou, 0.0

        # MODO RESTRICTED e não coletou tudo → reinicia fase
        pts_perdidos = total_pts_nivel - pts_coletados
        ratio = pts_perdidos / total_pts_nivel if total_pts_nivel else 0.0

        # zera progresso da fase
        self.current_points = self._points_at_level_start
        self.reload_level()
        return False, ratio

    def _blocked(self, x: int, y: int) -> bool:
        """True se coord é parede, água ou tranca."""
        tile = self.level.grid.tile(x, y)
        return tile in (Map.WALL, Map.WATER, Map.LOCK)

    def check_game_over(self) -> None:
        """Reinicia fase se o jogador ficar preso (sem movimentos)."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            nx, ny = self.player_x + dx, self.player_y + dy
            if not self.level.grid.inside(nx, ny):
                continue

            # (a) Tranca abrível
            if (
                self.level.grid.tile(nx, ny) is Map.LOCK
                and self.keys_obtained > 0
            ):
                return
            # (b) Tile livre
            if (
                not self._blocked(nx, ny)
                and (nx, ny) not in self.level.blocks
            ):
                return
            # (c) Bloco empurrável com espaço
            if (nx, ny) in self.level.blocks:
                bx, by = nx + dx, ny + dy
                if self.level.grid.inside(bx, by) and not self._blocked(bx, by):
                    return

        # → preso
        self.current_points = self._points_at_level_start
        self.reload_level()

    # --------------------------------------------------
    # Interações de coleta
    # --------------------------------------------------
    def check_coin_bag(self) -> None:
        for cb in list(self.level.coin_bags):  # copia p/ remover em loop
            if (self.player_x, self.player_y) == cb:
                self.current_points += 100
                self.level.coin_bags.remove(cb)
                break

    def check_key(self) -> None:
        for key in list(self.level.keys):
            if (self.player_x, self.player_y) == key:
                self.keys_obtained += 1
                self.level.keys.remove(key)
                break

    def check_lock(self, x: int, y: int) -> None:
        """Destranca vizinhança imediata se houver chave."""
        if self.keys_obtained == 0:
            return
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.level.grid.inside(nx, ny) and self.level.grid.tile(nx, ny) is Map.LOCK:
                self.level.grid.set_tile(nx, ny, Map.THIN_ICE)
                self.keys_obtained -= 1
                # pode destrancar só uma
                break

    # --------------------------------------------------
    # Movimento de blocos
    # --------------------------------------------------
    def _move_block(self, block: Tuple[int, int], direction: Tuple[int, int]) -> bool:
        bx, by = block
        dx, dy = direction
        nx, ny = bx + dx, by + dy

        # fora ou bloqueado → falha
        if not self.level.grid.inside(nx, ny) or self._blocked(nx, ny):
            return False

        # teleporte: atualiza destino
        if self.level.grid.tile(nx, ny) is Map.TELEPORT:
            idx = self.level.teleports.index((nx, ny))
            nx, ny = self.level.teleports[1 - idx]

        # move bloco
        self.level.blocks.remove(block)
        self.level.blocks.append((nx, ny))
        self.block_mov = ((nx, ny), direction)
        return True

    # --------------------------------------------------
    # Movimento do jogador
    # --------------------------------------------------
    def move_player(self, direction: Tuple[int, int]) -> None:
        dx, dy = direction
        nx, ny = self.player_x + dx, self.player_y + dy

        if not self.level.grid.inside(nx, ny):
            return  # fora do grid

        if self._blocked(nx, ny):
            return  # parede/água/tranca

        # Teleporte (entrada)
        if self.level.grid.tile(nx, ny) is Map.TELEPORT:
            idx = self.level.teleports.index((nx, ny))
            nx, ny = self.level.teleports[1 - idx]
            # converte ambos para TILE para evitar loop
            for tx, ty in self.level.teleports:
                self.level.grid.set_tile(tx, ty, Map.TILE)

        # Bloco empurrável
        if (nx, ny) in self.level.blocks:
            if not self._move_block((nx, ny), direction):
                return  # não pôde empurrar

        # Atualiza o tile que ficou para trás
        current_tile = self.level.grid.tile(self.player_x, self.player_y)
        if current_tile is Map.THIN_ICE:
            self.level.grid.set_tile(self.player_x, self.player_y, Map.WATER)
        elif current_tile is Map.THICK_ICE:
            self.level.grid.set_tile(self.player_x, self.player_y, Map.THIN_ICE)

        # Destranca vizinhança, se aplicável
        self.check_lock(nx, ny)

        # Teleporte (saída) – caso tenha caído num teleporte carregado por bloco
        if self.level.grid.tile(nx, ny) is Map.TELEPORT:
            idx = self.level.teleports.index((nx, ny))
            nx, ny = self.level.teleports[1 - idx]
            for tx, ty in self.level.teleports:
                self.level.grid.set_tile(tx, ty, Map.TILE)

        # Atualiza posição
        self.player_x, self.player_y = nx, ny
        self.current_points += 1
        self.current_tiles += 1

        # Coletas
        self.check_coin_bag()
        self.check_key()

    # --------------------------------------------------
    # Conveniências p/ renderização/AI
    # --------------------------------------------------
    @property
    def grid(self) -> Grid:
        return self.level.grid
