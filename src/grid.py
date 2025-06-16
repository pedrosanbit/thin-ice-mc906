from __future__ import annotations
from typing import List, Sequence

from src.mapping import Map


class Grid:
    """Wrapper seguro para a matriz de células.

    – Converte ints → Enum na construção
    – Garante verificação de limites em um só lugar
    – Centraliza leitura/escrita; evita IndexError disperso
    """

    def __init__(self, raw: Sequence[Sequence[int | Map]]):
        # Garante enum internamente
        self._cells: List[List[Map]] = [
            [Map(val) if not isinstance(val, Map) else val for val in row]
            for row in raw
        ]
        self.height = len(self._cells)
        self.width = len(self._cells[0])

    def inside(self, x: int, y: int) -> bool:
        """Retorna True se (x,y) estiver dentro dos limites."""
        return 0 <= x < self.width and 0 <= y < self.height

    def tile(self, x: int, y: int) -> Map:
        """Tile na coordenada (x,y). Lança IndexError se fora do grid."""
        if not self.inside(x, y):
            raise IndexError(f"({x}, {y}) fora do grid")
        return self._cells[y][x]

    def set_tile(self, x: int, y: int, value: Map) -> None:
        """Define o tile em (x,y)."""
        if not self.inside(x, y):
            raise IndexError(f"({x}, {y}) fora do grid")
        self._cells[y][x] = value

    def iter_coords(self):
        """Itera sobre todas as coordenadas, devolvendo (x,y,tile)."""
        for y in range(self.height):
            for x in range(self.width):
                yield x, y, self._cells[y][x]
